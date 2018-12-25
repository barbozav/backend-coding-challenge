import uuid

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from app.data.base import EventStore, EventStream
from app.data.errors import ConcurrencyError, NotFoundError, WriteError
from app.data.model import AggregateModel
from app.utils.logs import logger


class PostgresEventStore(EventStore):
    def __init__(self, session):
        self._session = session

    def load_stream(self, aggregate_uuid):
        try:
            aggregate = self._session.query(AggregateModel).options(
                joinedload('events')).filter(
                    AggregateModel.uuid == str(aggregate_uuid)).one()
        except NoResultFound:
            raise NotFoundError

        logger.debug(aggregate)

        version = aggregate.version
        events = [(row.event, row.data) for row in aggregate.events]

        return EventStream(version, events)

    def append_to_stream(self, aggregate_uuid, expected_version, events):
        connection = self._session.connection()

        if expected_version:
            sql = (f"UPDATE aggregates "
                   f"SET version = {expected_version} + 1 "
                   f"WHERE version = {expected_version} "
                   f"AND uuid = '{aggregate_uuid}'")
            result = connection.execute(sql)

            logger.debug(sql)
            logger.debug(result)

            if result.rowcount != 1:
                raise ConcurrencyError()
        else:
            sql = (f"INSERT INTO aggregates (uuid, version) "
                   f"VALUES ('{aggregate_uuid}', 1)")
            result = connection.execute(sql)

            logger.debug(sql)
            logger.debug(result)

            if result.rowcount != 1:
                raise WriteError()

        for event in events:
            sql = (f"INSERT INTO events (uuid, aggregate_uuid, event, data) "
                   f"VALUES ('{uuid.uuid4()}', '{aggregate_uuid}', "
                   f"'{event.__class__.__name__}', '{event.as_dict()}')")

            result = connection.execute(sql)

            logger.debug(sql)
            logger.debug(result)

            if result.rowcount != len(events):
                raise WriteError()
