from app.models.base import Aggregate
from app.models.errors import InvalidEventError
from app.models.events import (TranslationCreated, TranslationFinished,
                               TranslationPending, TranslationRequested)


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
            self.status = 'translated'
            self.finished = True
        else:
            raise InvalidEventError(f'Invalid event: {event}')
        self.changes.append(event)
