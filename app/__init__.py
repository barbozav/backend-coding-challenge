from dynaconf import FlaskDynaconf
from flask import Flask
from config import Config

import logging

app = Flask(__name__)
FlaskDynaconf(app)

app.logger.setLevel(logging.INFO)
app.logger.info('Unbabel Backend Coding Challenge startup')

from app import routes
