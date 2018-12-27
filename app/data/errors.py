from app.errors import ChallengeError


class EventStoreError(ChallengeError):
    """Base event store error."""


class ReadError(EventStoreError):
    """Raised when an error occurs on a read operation."""


class NotFoundError(ReadError):
    """Raised when trying to read an inexistent event stream."""


class WriteError(EventStoreError):
    """Raised when an error occurs on a write operation."""


class ConcurrencyError(WriteError):
    """Raised when a concurrency error occurs on a write operation."""
