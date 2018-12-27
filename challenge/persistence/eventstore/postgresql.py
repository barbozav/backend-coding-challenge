import json

from sqlalchemy.orm import joinedload, sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from challenge.persistence.eventstore.base import EventStore, EventStream
from challenge.persistence.eventstore.errors import (ConcurrencyError,
                                                     NotFoundError, WriteError)
from challenge.persistence.eventstore.model import AggregateModel
from challenge.utils.logging import logger


class PostgresEventStore(EventStore):
    def __init__(self, db):
        Session = sessionmaker()
        self._session = Session(bind=db)

    def load_stream(self, aggregate_uuid):
        try:
            aggregate = self._session.query(AggregateModel).options(
                joinedload('events')).filter(
                    AggregateModel.uuid == str(aggregate_uuid)).one()
        except NoResultFound:
            raise NotFoundError(f'Aggregate not found: {aggregate_uuid}')

        logger.info(f'Loading aggregate: {aggregate_uuid}')
        logger.debug(aggregate)

        version = aggregate.version
        events = aggregate.events

        return EventStream(version, events)

    def append_to_stream(self, aggregate_uuid, expected_version, events):
        if expected_version:
            sql = (f"UPDATE aggregates "
                   f"SET version = {expected_version} + 1 "
                   f"WHERE version = {expected_version} "
                   f"AND uuid = '{aggregate_uuid}'")
            result = self._session.execute(sql)

            logger.debug(sql)
            logger.debug(result)
            logger.info(f'Updated aggregate: {aggregate_uuid}')

            if result.rowcount != 1:
                raise ConcurrencyError(
                    'Failed to update aggregate in database.')
        else:
            sql = (f"INSERT INTO aggregates (uuid, version) "
                   f"VALUES ('{aggregate_uuid}', 1)")
            result = self._session.execute(sql)

            logger.debug(sql)
            logger.debug(result)
            logger.info(f'Created aggregate: {aggregate_uuid}')

            if result.rowcount != 1:
                raise WriteError('Failed to insert aggregate into database.')

        for event in events:
            sql_values = (f"VALUES('{event.id}', '{aggregate_uuid}', "
                          f"'{event.__class__.__name__}', "
                          f"'{json.dumps(event.as_dict())}')")

            sql = (f"INSERT INTO events (uuid, aggregate_uuid, event, data) "
                   f"{sql_values} ON CONFLICT (uuid) DO NOTHING")

            result = self._session.execute(sql)

            logger.debug(sql)
            logger.debug(result)
            if result.rowcount:
                logger.info(f'Created event: {event.id}')

        self._session.commit()
