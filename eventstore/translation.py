from attr import attrib, attrs

from eventstore.base import Aggregate, Event


@attrs(frozen=True)
class TranslationCreated(Event):
    text = attrib(type=str)


@attrs(frozen=True)
class TranslationRequested(Event):
    id = attrib(type=int)


@attrs(frozen=True)
class TranslationPending(Event):
    pass


@attrs(frozen=True)
class TranslationFinished(Event):
    translated_text = attrib(type=str)


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
            self.id = event.id
            self.status = 'requested'
        elif isinstance(event, TranslationPending):
            self.status = 'pending'
        elif isinstance(event, TranslationFinished):
            self.translated_text = event.translated_text
            self.status = 'translated'
        else:
            raise ValueError('Unknown event!')
        self.changes.append(event)
