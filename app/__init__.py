import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dynaconf import FlaskDynaconf
from flask import Flask

import logging

app = Flask(__name__)
FlaskDynaconf(app)

app.logger.setLevel(logging.INFO)
app.logger.info('Unbabel Backend Coding Challenge startup')

broker = RedisBroker(url='redis://redis:6379')
dramatiq.set_broker(broker)

from app import routes
