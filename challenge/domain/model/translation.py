from attr import attrib, attrs

from challenge.domain.model.base import Aggregate, Event
from challenge.domain.model.errors import InvalidEventError


@attrs(frozen=True)
class TranslationCreated(Event):
    text = attrib(type=str)


@attrs(frozen=True)
class TranslationRequested(Event):
    translation_id = attrib(type=int)


@attrs(frozen=True)
class TranslationPending(Event):
    pass


@attrs(frozen=True)
class TranslationFinished(Event):
    translated_text = attrib(type=str)


@attrs(frozen=True)
class TranslationAborted(Event):
    error = attrib(type=str)


class Translation(Aggregate):
    @classmethod
    def create(cls, text):
        event = TranslationCreated.create(text)
        return super().create([event])

    def apply(self, event):
        if isinstance(event, TranslationCreated):
            self.text = event.text
            self.status = 'created'
        elif isinstance(event, TranslationRequested):
            self.translation_id = event.translation_id
            self.status = 'requested'
        elif isinstance(event, TranslationPending):
            self.status = 'pending'
        elif isinstance(event, TranslationFinished):
            self.translated_text = event.translated_text
            self.status = 'finished'
            self.finished = True
        elif isinstance(event, TranslationAborted):
            self.error = event.error
            self.status = 'aborted'
            self.finished = True
        else:
            raise InvalidEventError(f'Invalid event: {event}')
        self.changes.append(event)
