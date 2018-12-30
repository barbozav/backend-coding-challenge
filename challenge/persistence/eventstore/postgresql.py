import json

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from challenge.persistence.eventstore.base import EventStore, EventStream
from challenge.persistence.eventstore.errors import (ConcurrencyError,
                                                     NotFoundError, WriteError)
from challenge.persistence.eventstore.model import AggregateModel
from challenge.utils.logging import logger


class PostgresEventStore(EventStore):
    def load_stream(self, session, aggregate_uuid):
        try:
            aggregate = session.query(AggregateModel).options(
                joinedload('events')).filter(
                    AggregateModel.uuid == str(aggregate_uuid)).one()
        except NoResultFound:
            raise NotFoundError(f'Aggregate not found: {aggregate_uuid}')

        version = aggregate.version
        events = aggregate.events
        event_stream = EventStream(version, events)

        logger.info(f'loaded aggregate: {aggregate_uuid}')
        logger.debug(event_stream)

        return event_stream

    def append_to_stream(self, session, aggregate_uuid, expected_version,
                         events):
        if expected_version:
            sql = (f"UPDATE aggregates "
                   f"SET version = {expected_version} + 1 "
                   f"WHERE version = {expected_version} "
                   f"AND uuid = '{aggregate_uuid}'")

            result = session.execute(sql)

            logger.info(f'updated aggregate: {aggregate_uuid}')
            logger.debug(sql)

            if result.rowcount != 1:
                raise ConcurrencyError(
                    'Failed to update aggregate in database.')

        else:
            sql = (f"INSERT INTO aggregates (uuid, version) "
                   f"VALUES ('{aggregate_uuid}', 1)")

            result = session.execute(sql)

            if result.rowcount != 1:
                raise WriteError('Failed to insert aggregate into database.')

            logger.info(f'new aggregate: {aggregate_uuid}')
            logger.debug(sql)

        for event in events:
            values = (f"('{event.id}', '{aggregate_uuid}', "
                      f"'{event.__class__.__name__}', "
                      f"'{json.dumps(event.as_dict())}')")

            sql = (f"INSERT INTO events (uuid, aggregate_uuid, event, data) "
                   f"VALUES {values} ON CONFLICT (uuid) DO NOTHING")

            result = session.execute(sql)

            logger.debug(result)

            if result.rowcount:
                logger.info(f'new event: {event.id}')
            logger.debug(sql)
