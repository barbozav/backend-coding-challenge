class AggregateError(Exception):
    """Base event sourced aggregate error."""


class InvalidEventError(AggregateError, ValueError):
    """Raised when attempting to apply an invalid event."""


class TranslationError(AggregateError):
    """Base Translation error."""


class AlreadyFinishedError(TranslationError):
    """Raised when attempting to change a finished translation."""
