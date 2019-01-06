import time

import dramatiq
from dynaconf import settings

from challenge.application import app, projections, repository  # noqa:F401
from challenge.domain.model.translation import (
    TranslationAborted, TranslationFinished, TranslationPending)
from challenge.domain.services.unbabel.client import Client

_translation_pending = ['new', 'accepted', 'translating']
_translation_finished = ['rejected', 'canceled', 'failed', 'completed']

_client = Client(
    client=settings.API_CLIENT, token=settings.API_TOKEN, url=settings.API_URL)


@dramatiq.actor
def projections_task(id):
    """ Task for updating the read-model of an aggregate.

    As the read-model doesn't need to be updated in real-time, a worker
    is scheduled to do these updates when possible.

    Args:
        id (string): An aggregate UUID4 string.
    """
    projections.update(id)


@dramatiq.actor
def translation_task(id):
    """ Task for processing a translation.

    This task is responsible for requesting the translation service to
    translated a given text from English to Spanish.

    The Translation aggregate is already created and persisted, so this
    task must fetch its data. If for some reason the application goes
    down, it's possible to reprocess "requested" translations adding
    their IDs to the workers queue.

    After sending a request to the translation service, this worker will
    persist a tracking identifier and poll this translation until it's
    finished.

    Args:
        id (string): The translation aggregate UUID4 string.
    """
    translation = repository.get(id)

    response_json = _client.request_translation(translation.text,
                                                settings.API_SOURCE_LANGUAGE,
                                                settings.API_TARGET_LANGUAGE)

    uid = response_json['uid']
    status = response_json['status']

    if status in _translation_pending:
        event = TranslationPending.create(uid)
        translation.apply(event)
        repository.save(translation)
        _poll_translation(id)
    else:
        event = TranslationAborted.create(
            f''Translation service request failed.'')
        translation.apply(event)
        repository.save(translation)

    projections_task.send(id)


def _poll_translation(id):
    """Check the translation service ID every 5 seconds.

    Apply events to the aggregate whenever there are relevant changes in
    the translation service processing status.

    """
    translation = repository.get(id)
    while True:
        response_json = _client.get_translation(translation.translation_id)
        status = response_json['status']
        if (status in _translation_pending) and (translation.status !=
                                                 'pending'):
            translation = repository.get(id)
            event = TranslationPending.create()
            translation.apply(event)
            repository.save(translation)
            projections_task.send(id)
        elif (status in _translation_finished) and (translation.status !=
                                                    'finished'):
            translation = repository.get(id)
            event = TranslationFinished.create(response_json['translatedText'])
            translation.apply(event)
            repository.save(translation)
            projections_task.send(id)
            break
        time.sleep(5)
