from functools import singledispatch

from attr import attrib, attrs
from dynaconf import settings

from challenge.domain.model.translation import (
    TranslationFinished, TranslationPending, TranslationRequested)
from challenge.persistence import session_scope
from challenge.utils.logging import logger


@attrs(frozen=True)
class Pagination:
    """A simple pagination helper.

    Attributes:
        items (Query): "translations" table queried rows.
        total (int): "translations" table total count of rows.
        page (int): Instance page.

    """

    items = attrib()
    total = attrib()
    page = attrib()

    @property
    def has_prev(self):
        """Return true if there's a previous page."""
        return self.page > 1

    @property
    def prev_page(self):
        """Return the previous page number if it exists."""
        return self.page - 1 if self.has_prev else None

    @property
    def has_next(self):
        """Return true if there's a next page."""
        limit = self.page * settings.TRANSLATIONS_PER_PAGE
        return limit < self.total

    @property
    def next_page(self):
        """Return the next page number if it exists."""
        return self.page + 1 if self.has_next else None


class TranslationProjections:
    """Interface between the application layer and persistence layer.

    It translates the domain layer models to persistence data models.

    For now we have a Translation projection for visualization, but it
    could be expanded for other projections as auditing or data
    analysis.

    Args:
        read_model: The translations projection (read-model).

    """

    def __init__(self, read_model):
        self._read_model = read_model

    def paginate(self, page=1):
        """Get all translation items from a single page.

        Args:
            page (int): Page number.

        """
        with session_scope() as session:
            total = self._read_model.count(session)
            items = self._read_model.get(session, page)

        return Pagination(items=items, total=total, page=page)

    def handle(self, aggregate_uuid, event):
        """Handle events and update the projections.

        Received an event, it decides whether insert a new projection
        or update the existing ones accordingly.

        Args:
            aggregate_uuid (str): An UUID4 string to which aggregate
                projection should be update.
            event (Event): An `Event` to handle. The read-model data
                persistence operation is chosen based on this event.

        """

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
