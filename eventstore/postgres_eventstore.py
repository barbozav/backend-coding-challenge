from eventstore import EventStore, EventStream


class PostgreSQLEventStore(EventStore):
    def __init__(self, session: Session):
        self.session = session  # we rely on SQLAlchemy, so we need Session to be passed for future usage

    def load_stream(self, aggregate_uuid: uuid.UUID):
        try:
            aggregate: AggregateModel = self.session.query(  # we query for aggregate with its events
                AggregateModel).options(joinedload('events')).filter(
                    AggregateModel.uuid == str(aggregate_uuid)).one()
        except exc.NoResultFound:  # we do not allow sqlalchemy-specific exception to reach our code level higher
            raise NotFound

        # translate all events models to proper event objects (see part 1)
        events_objects = [
            self._translate_to_object(model) for model in aggregate.events
        ]
        version = aggregate.version

        return EventsStream(events_objects, version)

    def _translate_to_object(self, event_model: EventModel) -> Event:
        """This method is responsible for translating models to event classes instances"""
        class_name = event_model.name
        kwargs = event_model.data
        # assuming `events` is a module containing all events classes we can easily get
        # desired class by its name saved along with event data
        event_class: typing.Type[Event] = getattr(events, class_name)
        return event_class(**kwargs)

    def append_to_stream(self, aggregate_uuid: uuid.UUID,
                         expected_version: typing.Optional[int],
                         events: typing.List[Event]):
        # returns connection within session (same transaction state)
        connection = self.session.connection()

        if expected_version:  # an update
            stmt = AggregateModel.__table__.update().values(
                version=expected_version +
                1).where((AggregateModel.version == expected_version) &
                         (AggregateModel.uuid == str(aggregate_uuid)))
            result_proxy = connection.execute(stmt)

            if result_proxy.rowcount != 1:  # 1
                raise ConcurrentStreamWriteError
        else:  # new aggregate
            stmt = AggregateModel.__table__.insert().values(
                uuid=str(aggregate_uuid), version=1)
            connection.execute(stmt)

        for event in events:
            aggregate_uuid_str = str(aggregate_uuid)
            event_as_dict = event.as_dict()

            connection.execute(EventModel.__table__.insert().values(
                uuid=str(uuid.uuid4()),
                aggregate_uuid=aggregate_uuid_str,
                name=event.__class__.__name__,
                data=event_as_dict))

            payload = json.dumps(event_as_dict)
            connection.execute(
                f'NOTIFY events, \'{aggregate_uuid_str}_{event.__class__.__name__}_{payload}\''
            )
