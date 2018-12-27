import dramatiq

from app import app
from app.external import unbabel


@dramatiq.actor
def translate(text):
    client = unbabel.Client()
    json = client.request_translation(text)
    app.logger.info(f'Requested translation: {json}')


@dramatiq.actor
def poll_translation(id):
    pass
