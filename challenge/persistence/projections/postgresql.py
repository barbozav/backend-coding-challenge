from dynaconf import settings

from challenge.persistence.projections.model import TranslationModel
from challenge.utils.logging import logger


class PostgresTranslation:
    """PostgreSQL queries for the "translations" table."""

    def get(self, session, page=1, per_page=None):
        """Query "translations" rows ordered and limited by pagination.

        Args:
            session (Session): A session context into which operate.
            page (int): The page number to set the query offset.
            per_page (int): The number of rows per page to limit the
                query.

        Returns:
            Query: `per_page` rows ordered by `translated_text`
                ascending.

        """
        per_page = per_page or settings.TRANSLATIONS_PER_PAGE

        return session.query(TranslationModel).order_by(
            TranslationModel.length.asc()()).limit(
                settings.TRANSLATIONS_PER_PAGE).offset(
                    (page - 1) * settings.TRANSLATIONS_PER_PAGE)

    def count(self, session):
        """Count the number of "translations" rows.

        Args:
            session (Session): A session context into which operate.

        Returns:
            int: number of rows in the "translations" table.

        """
        return session.query(TranslationModel).count()

    def create(self, session, aggregate_uuid, text):
        """Insert a newly created aggregate in the "translations" table.

        Args:
            session (Session): A session context into which operate.
            aggregate_uuid (str): An UUID4 string. It must match its
                respective event sourced aggregate.
            text (str): The text sent to the translation service.

        """
        # Newly created translations have a `translated_text`` length
        # automatically set to 0, putting them in the beginning of the
        # first page for visualization (and tracking its status).
        values = (f"('{aggregate_uuid}', 'requested', 0, '{text}')")
        sql = (f'INSERT INTO translations (uuid, status, length, text) '
               f'VALUES {values} ON CONFLICT DO NOTHING')

        session.execute(sql)

        logger.debug(sql)

    def update_to_pending(self, session, aggregate_uuid):
        """Update a translation aggregate status to "pending".

        Args:
            session (Session): A session context into which operate.
            aggregate_uuid (str): An UUID4 string. It must match its
                respective event sourced aggregate.

        """
        sql = (f"UPDATE translations "
               f"SET status = 'pending' "
               f"WHERE uuid = '{aggregate_uuid}'")

        session.execute(sql)

        logger.debug(sql)

    def update_to_finished(self, session, aggregate_uuid, translated_text):
        """Update a translation aggregate status to "finished".

        Args:
            session (Session): A session context into which operate.
            aggregate_uuid (str): An UUID4 string. It must match its
                respective event sourced aggregate.

        """
        sql = (f"UPDATE translations "
               f"SET status = 'finished', "
               f"SET length = {len(translated_text)}, "
               f"translated_text = '{translated_text}' "
               f"WHERE uuid = '{aggregate_uuid}'")

        session.execute(sql)

        logger.debug(sql)
