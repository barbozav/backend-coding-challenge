import time

import dramatiq
from dynaconf import settings
from flask_sse import sse

from challenge.application import app, projections, repository
from challenge.domain.model.translation import (
    TranslationAborted, TranslationFinished, TranslationPending)
from challenge.domain.services.unbabel.client import Client

from challenge.utils.logging import logger

_client = Client(
    client=settings.API_CLIENT, token=settings.API_TOKEN, url=settings.API_URL)


def _translation_pending(status):
    new = (status == 'new')
    accepted = (status == 'accepted')
    translating = (status == 'translating')
    return new or accepted or translating


def _translation_finished(status):
    rejected = (status == 'rejected')
    canceled = (status == 'canceled')
    failed = (status == 'failed')
    completed = (status == 'completed')
    return rejected or canceled or failed or completed


def _poll_translation(id):
    translation = repository.get(id)
    while True:
        response_json = _client.get_translation(translation.translation_id)
        status = response_json['status']
        if _translation_pending(status) and translation.status != 'pending':
            translation = repository.get(id)
            event = TranslationPending.create()
            translation.apply(event)
            repository.save(translation)
            projections.handle(id, event)
            with app.app_context():
                sse.publish({'id': f'{id}'})
        elif _translation_finished(
                status) and translation.status != 'finished':
            translation = repository.get(id)
            event = TranslationFinished.create(response_json['translatedText'])
            translation.apply(event)
            repository.save(translation)
            projections.handle(id, event)
            with app.app_context():
                sse.publish({'id': f'{id}'})
            break
        time.sleep(2)


@dramatiq.actor
def translation_task(id):
    translation = repository.get(id)
    response_json = _client.request_translation(translation.text)

    uid = response_json['uid']
    status = response_json['status']

    if _translation_pending(status):
        event = TranslationPending.create(uid)
        translation.apply(event)
        repository.save(translation)
        _poll_translation(id)
    else:
        event = TranslationAborted.create('Failed to request translation.')
        translation.apply(event)
        repository.save(translation)

    projections.handle(id, event)
