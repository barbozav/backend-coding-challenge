from app.data.postgresql import PostgresEventStore
from app.models import events
from app.models.translation import Translation


class AggregatesRepository:
    def __init__(self, aggregate_cls, event_store):
        self._aggregate_cls = aggregate_cls
        self._event_store = event_store

    def get(self, aggregate_uuid):
        events_stream = self._event_store.load_stream(aggregate_uuid)
        stream_events = self._event_row_to_object(events_stream.events)

        aggregate = self._aggregate_cls(aggregate_uuid, events_stream.version)

        for event in stream_events:
            aggregate.apply(event)

        return aggregate

    def save(self, aggregate):
        self._event_store.append_to_stream(aggregate.id, aggregate.version,
                                           aggregate.changes)

    def _event_row_to_object(self, event_rows):
        event_objects = []
        for row in event_rows:
            event_cls = getattr(events, row.event)
            kwargs = row.data
            kwargs['id'] = row.uuid

            instance = event_cls(**kwargs)

            event_objects.append(instance)

        return event_objects


translations_repository = AggregatesRepository(Translation,
                                               PostgresEventStore())
