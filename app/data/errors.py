class EventStoreError(Exception):
    """Base event store error."""


class ReadError(EventStoreError):
    """Raised when an error occurs on a read operation."""


class WriteError(EventStoreError):
    """Raised when an error occurs on a write operation."""


class ConcurrencyError(WriteError):
    """Raised when a concurrency error occurs on a write operation."""


class DuplicateIdError(WriteError):
    """Raised when inserting an event stream with a duplicate id."""


class NotFoundError(ReadError):
    """Raised when trying to read an inexistent event stream."""
