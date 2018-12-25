from app.models import events


class AggregatesRepository:
    def __init__(self, aggregate_cls, event_store):
        self._aggregate_cls = aggregate_cls
        self._event_store = event_store

    def get(self, aggregate_uuid):
        events_stream = self._event_store.load_stream(aggregate_uuid)
        stream_events = self._event_data_to_object(events_stream.events)

        aggregate = self._aggregate_cls.create(aggregate_uuid)

        aggregate.version = events_stream.version

        for event in stream_events:
            aggregate.apply(event)

        return aggregate

    def save(self, aggregate):
        self._event_store.append_to_stream(aggregate.id, aggregate.version,
                                           aggregate.changes)

    def _event_data_to_object(self, events_data):
        event_objects = []
        for (event, data) in events_data:
            event_cls = getattr(events, event)
            kwargs = data

            instance = event_cls(**kwargs)

            event_objects.append(instance)

        return event_objects
