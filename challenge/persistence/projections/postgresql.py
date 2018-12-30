from challenge.utils.logging import logger
from challenge.persistence.projections.model import TranslationModel
from dynaconf import settings


class PostgresTranslation:
    def get(self, session, page):
        return session.query(TranslationModel).order_by(
            TranslationModel.length.desc()).limit(
                settings.TRANSLATIONS_PER_PAGE).offset(
                    (page - 1) * settings.TRANSLATIONS_PER_PAGE)

    def count(self, session):
        return session.query(TranslationModel).count()

    def create(self, session, aggregate_uuid, text):
        values = (f"('{aggregate_uuid}', 'requested', {len(text)}, "
                  f"'{text}')")
        sql = (f"INSERT INTO translations (uuid, status, length, text) "
               f"VALUES {values} ON CONFLICT DO NOTHING")

        session.execute(sql)

        logger.debug(sql)

    def update_to_pending(self, session, aggregate_uuid):
        sql = (f"UPDATE translations "
               f"SET status = 'pending' "
               f"WHERE uuid = '{aggregate_uuid}'")

        session.execute(sql)

        logger.debug(sql)

    def update_to_finished(self, session, aggregate_uuid, translated_text):
        sql = (f"UPDATE translations "
               f"SET status = 'finished', "
               f"translated_text = '{translated_text}' "
               f"WHERE uuid = '{aggregate_uuid}'")

        session.execute(sql)

        logger.debug(sql)
