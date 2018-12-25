from attr import attrib, attrs

from domain.model.base import Event


@attrs(frozen=True)
class TranslationCreated(Event):
    text = attrib(type=str)


@attrs(frozen=True)
class TranslationRequested(Event):
    unbabel_id = attrib(type=int)


@attrs(frozen=True)
class TranslationPending(Event):
    pass


@attrs(frozen=True)
class TranslationFinished(Event):
    translated_text = attrib(type=str)
