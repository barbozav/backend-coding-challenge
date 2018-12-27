from abc import ABC, abstractmethod

from attr import attrib, attrs


@attrs
class EventStream:
    version = attrib()
    events = attrib()


class EventStore(ABC):
    @abstractmethod
    def load_stream(self, uuid):
        pass

    @abstractmethod
    def append_to_stream(self, uuid, version, events):
        pass
