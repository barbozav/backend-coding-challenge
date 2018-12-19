import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from attr import attrib, attrs


@attrs(frozen=True)
class Event():
    created_at = attrib()

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(datetime.utcnow().isoformat(), *args, **kwargs)


class Aggregate(ABC):
    def __init__(self, uid, version):
        self.uid = uid
        self.version = version
        self.changes = []

    @classmethod
    def create(cls, events):
        uid = str(uuid.uuid4())
        instance = cls(uid, None)
        for event in events:
            instance.apply(event)
        return instance

    @abstractmethod
    def apply(self, event):
        pass
