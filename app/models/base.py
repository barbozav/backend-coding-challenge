import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from attr import asdict, attrib, attrs


@attrs(frozen=True)
class Event(ABC):
    id = attrib()
    occurred_at = attrib()

    @classmethod
    def create(cls, *args, **kwargs):
        event_uuid = str(uuid.uuid4())
        occurred_at = datetime.utcnow().isoformat()
        return cls(event_uuid, occurred_at, *args, **kwargs)

    def as_dict(self):
        return asdict(self)


class Aggregate(ABC):
    def __init__(self, aggregate_uuid, version=None):
        self._id = aggregate_uuid
        self._version = version
        self._changes = []

    @property
    def id(self):
        return self._id

    @property
    def version(self):
        return self._version

    @property
    def changes(self):
        return self._changes

    @classmethod
    def create(cls, events):
        aggregate_uuid = str(uuid.uuid4())

        instance = cls(aggregate_uuid)

        for event in events:
            instance.apply(event)
        return instance

    @abstractmethod
    def apply(self, event):
        pass
