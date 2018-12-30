from functools import singledispatch

from attr import attrib, attrs

from challenge.domain.model.base import Aggregate, Event
from challenge.domain.model.errors import InvalidEventError
from challenge.utils.logging import logger


@attrs(frozen=True)
class TranslationRequested(Event):
    text = attrib(type=str)


@attrs(frozen=True)
class TranslationPending(Event):
    translation_id = attrib(type=int)


@attrs(frozen=True)
class TranslationFinished(Event):
    translated_text = attrib(type=str)


@attrs(frozen=True)
class TranslationAborted(Event):
    error = attrib(type=str)


class Translation(Aggregate):
    @classmethod
    def create(cls, text):
        logger.info(f'creating aggregate')
        event = TranslationRequested.create(text)
        return super().create([event])

    def apply(self, event):
        @singledispatch
        def _apply(_event):
            raise InvalidEventError(f'Invalid event: {_event}')

        @_apply.register(TranslationRequested)
        def _(_event):
            self.text = _event.text
            self.status = 'requested'

        @_apply.register(TranslationPending)
        def _(_event):
            self.translation_id = _event.translation_id
            self.status = 'pending'

        @_apply.register(TranslationFinished)
        def _(_event):
            self.translated_text = _event.translated_text
            self.status = 'finished'
            self.finished = True

        @_apply.register(TranslationAborted)
        def _(_event):
            self.error = _event.error
            self.status = 'aborted'
            self.finished = True

        logger.info(f'applying event ({event.id}) on aggregate: {self.id}')
        logger.debug(event.as_dict())

        _apply(event)
        self.changes.append(event)
