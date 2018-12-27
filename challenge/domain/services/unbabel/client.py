from urllib.parse import urljoin

import requests

SANDBOX_API_URL = 'https://sandbox.unbabel.com/tapi/v2/'


class Client:
    def __init__(self, client, token, url=SANDBOX_API_URL):

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
            'target_language': target_language
        }

        return self._post(url, payload).json()

    def get_translation(self, id):

        url = urljoin(self._url, f'translation/{id}')
        return self._get(url).json()
