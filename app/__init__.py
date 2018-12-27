import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dynaconf import FlaskDynaconf
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

import logging

app = Flask(__name__)
Bootstrap(app)
FlaskDynaconf(app)
app.logger.setLevel(logging.DEBUG)
app.logger.info('Unbabel Backend Coding Challenge startup')

db = SQLAlchemy(app)
from app.data import model
db.create_all()


broker = RedisBroker(url='redis://redis:6379')
dramatiq.set_broker(broker)

from app.resources import routes
