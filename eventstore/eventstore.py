class ConcurrentStreamWriteError(RuntimeError):
    pass


class EventStream:
    events: typing.List[Event]
    version: int

    def __init__(self, events, version):
        pass


class EventStore(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def load_stream(self, aggregate_uuid: uuid.UUID) -> EventStream:
        pass

    @abc.abstractmethod
    def append_to_stream(self, aggregate_uuid: uuid.UUID,
                         expected_version: typing.Optional[int],
                         events: typing.List[Event]) -> None:
        pass
