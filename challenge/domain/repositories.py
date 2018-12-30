from challenge.domain.model import translation
from challenge.persistence import session_scope
from challenge.utils.logging import logger


class AggregatesRepository:
    def __init__(self, aggregate_cls, event_store):
        self._aggregate_cls = aggregate_cls
        self._event_store = event_store

    def get(self, aggregate_uuid):
        logger.info(f'loading aggregate: {aggregate_uuid}...')

        with session_scope() as session:
            events_stream = self._event_store.load_stream(
                session, aggregate_uuid)
            stream_events = self._event_row_to_object(events_stream.events)

            aggregate = self._aggregate_cls(aggregate_uuid,
                                            events_stream.version)

            for event in stream_events:
                aggregate.apply(event)

        return aggregate

    def save(self, aggregate):
        logger.info(f'saving aggregate: {aggregate.id}...')
        with session_scope() as session:
            self._event_store.append_to_stream(
                session, aggregate.id, aggregate.version, aggregate.changes)

    def _event_row_to_object(self, event_rows):
        event_objects = []
        for row in event_rows:
            event_cls = getattr(translation, row.event)
            kwargs = row.data
            kwargs['id'] = row.uuid

            instance = event_cls(**kwargs)

            event_objects.append(instance)

        return event_objects
