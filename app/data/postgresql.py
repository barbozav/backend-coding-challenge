import json

from app import app, db
from app.data.base import EventStore, EventStream
from app.data.errors import ConcurrencyError, NotFoundError, WriteError
from app.data.model import AggregateModel


class PostgresEventStore(EventStore):
    def load_stream(self, aggregate_uuid):
        try:
            aggregate = db.session.query(AggregateModel).options(
                db.joinedload('events')).filter(
                    AggregateModel.uuid == str(aggregate_uuid)).one()
        except db.NoResultFound:
            raise NotFoundError(f'Aggregate not found: {aggregate_uuid}')

        app.logger.info(f'Loading aggregate: {aggregate_uuid}')
        app.logger.debug(aggregate)

        version = aggregate.version
        events = aggregate.events

        return EventStream(version, events)

    def append_to_stream(self, aggregate_uuid, expected_version, events):
        if expected_version:
            sql = (f"UPDATE aggregates "
                   f"SET version = {expected_version} + 1 "
                   f"WHERE version = {expected_version} "
                   f"AND uuid = '{aggregate_uuid}'")
            result = db.session.execute(sql)

            app.logger.debug(sql)
            app.logger.debug(result)
            app.logger.info(f'Updated aggregate: {aggregate_uuid}')

            if result.rowcount != 1:
                raise ConcurrencyError(
                    'Failed to update aggregate in database.')
        else:
            sql = (f"INSERT INTO aggregates (uuid, version) "
                   f"VALUES ('{aggregate_uuid}', 1)")
            result = db.session.execute(sql)

            app.logger.debug(sql)
            app.logger.debug(result)
            app.logger.info(f'Created aggregate: {aggregate_uuid}')

            if result.rowcount != 1:
                raise WriteError('Failed to insert aggregate into database.')

        for event in events:
            sql_values = (f"VALUES('{event.id}', '{aggregate_uuid}', "
                          f"'{event.__class__.__name__}', "
                          f"'{json.dumps(event.as_dict())}')")

            sql = (f"INSERT INTO events (uuid, aggregate_uuid, event, data) "
                   f"{sql_values} ON CONFLICT (uuid) DO NOTHING")

            result = db.session.execute(sql)

            app.logger.debug(sql)
            app.logger.debug(result)
            if result.rowcount:
                app.logger.info(f'Created event: {event.id}')

        db.session.commit()
