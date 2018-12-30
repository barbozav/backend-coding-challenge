from functools import singledispatch

from dynaconf import settings

from challenge.domain.model.translation import (
    TranslationFinished, TranslationPending, TranslationRequested)
from challenge.utils.logging import logger
from challenge.persistence import session_scope


class TranslationProjections:
    def __init__(self, read_model):
        self._read_model = read_model

    def paginate(self, page=1):
        with session_scope() as session:
            count = self._read_model.count(session)
            items = self._read_model.get(session, page)

            prev_page = page - 1 if page > 1 else None

            if page * settings.TRANSLATIONS_PER_PAGE < count:
                next_page = page + 1
            else:
                next_page = None

            pagination = {
                'items': items,
                'has_prev': prev_page is not None,
                'prev_page': prev_page,
                'has_next': next_page is not None,
                'next_page': next_page
            }

            return pagination

    def has_hext(self, page):
        with session_scope() as session:
            self._read_model.get(session, page)

    def handle(self, aggregate_uuid, event):
        @singledispatch
        def _handle(_event):
            pass

        @_handle.register(TranslationRequested)
        def _(_event):
            with session_scope() as session:
                self._read_model.create(session, aggregate_uuid, _event.text)

        @_handle.register(TranslationPending)
        def _(_event):
            with session_scope() as session:
                self._read_model.update_to_pending(session, aggregate_uuid)

        @_handle.register(TranslationFinished)
        def _(_event):
            with session_scope() as session:
                self._read_model.update_to_finished(session, aggregate_uuid,
                                                    _event.translated_text)

        logger.info(f'updating projection: {aggregate_uuid}')
        _handle(event)
