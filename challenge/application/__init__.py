import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dynaconf import FlaskDynaconf, settings
from flask import Flask
from flask.logging import default_handler
from flask_bootstrap import Bootstrap

from challenge.domain.model.translation import Translation
from challenge.domain.repositories import AggregatesRepository
from challenge.persistence import create_db, create_tables
from challenge.persistence.eventstore import model  # noqa: F401
from challenge.persistence.eventstore.postgresql import PostgresEventStore


def create_repository():
    db = create_db()
    create_tables(db)

    repo = AggregatesRepository(Translation, PostgresEventStore(db))
    return repo


def setup_worker():
    broker = RedisBroker(url=f'{settings.BROKER_URI}')
    dramatiq.set_broker(broker)


def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    FlaskDynaconf(app)

    app.logger.removeHandler(default_handler)

    return app


repository = create_repository()
setup_worker()
app = create_app()

from challenge.application import routes  # noqa: F401
