from urllib.parse import urljoin

import requests
from dynaconf import settings

api_client = settings.get('API_CLIENT')
api_token = settings.get('API_TOKEN')
api_url = settings.get('API_URL')


class Client(object):
    def __init__(self, client=api_client, token=api_token, url=api_url):

        self._url = url

        self._headers = {
            'Content-Type': 'application/json',
            'Authorization': f'ApiKey {client}:{token}'
        }

    def _get(self, url):
        return requests.get(url, headers=self._headers)

    def _post(self, url, payload):
        return requests.post(url, json=payload, headers=self._headers)

    def request_translation(self,
                            input,
                            source_language='en',
                            target_language='es'):

        url = urljoin(self._url, 'translation')

        payload = {
            'text': input,
            'source_language': source_language,
            'target_language': target_language,
            'callback_url': 'http://8d41ef9e.ngrok.io'
        }

        return self._post(url, payload).json()

    def get_translation(self, id):

        url = urljoin(self._url, f'translation/{id}')
        return self._get(url).json()
