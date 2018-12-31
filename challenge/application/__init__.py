import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dynaconf import FlaskDynaconf, settings
from flask import Flask
from flask.logging import default_handler
from flask_bootstrap import Bootstrap
from flask_sse import sse

from challenge.domain.model.translation import Translation
from challenge.domain.projections import TranslationProjections
from challenge.domain.repositories import AggregatesRepository
from challenge.persistence import create_db, create_tables
from challenge.persistence.eventstore import model as e_model  # noqa: F401
from challenge.persistence.eventstore.postgresql import PostgresEventStore
from challenge.persistence.projections import model as p_model  # noqa: F401
from challenge.persistence.projections.postgresql import PostgresTranslation
from challenge.utils.logging import logger


def setup_database():
    logger.info('creating databases')
    db = create_db()
    create_tables(db)


def create_repository():
    logger.info('creating event sourced repositories')
    return AggregatesRepository(Translation, PostgresEventStore())


def create_projections():
    logger.info('creating read model projections')
    return TranslationProjections(PostgresTranslation())


def setup_worker():
    logger.info('creating tasks queue')
    broker = RedisBroker(url=f'{settings.REDIS_URL}')
    dramatiq.set_broker(broker)


def create_app():
    logger.info('starting application')
    app = Flask(__name__)
    Bootstrap(app)
    FlaskDynaconf(app)
    app.register_blueprint(sse, url_prefix='/stream')

    app.logger.removeHandler(default_handler)

    return app


db = setup_database()
repository = create_repository()
projections = create_projections()
setup_worker()
app = create_app()

from challenge.application import routes  # noqa: F401
