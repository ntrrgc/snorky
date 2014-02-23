import requests
import simplejson as json

class MiauBackendConnector(object):
    def __init__(self, url_base, secret_key):
        self.url_base = url_base
        self.secret_key = secret_key
    
        self.websession = requests.session()

    def talk_to_miau_server(self, url, data):
        response = self.websession.post(self.url_base + url,
                data=json.dumps(data), auth=(self.secret_key,''))
        return response

    def send_delta(self, created=[], updated=[], deleted=[]):
        response = self.talk_to_miau_server('notify_delta', {
            'created': created if isinstance(created, list) else [created],
            'updated': updated if isinstance(updated, list) else [updated],
            'deleted': deleted if isinstance(deleted, list) else [deleted],
        })

        # Raise an error if the server does not reply with 204 (OK, Empty Response)
        if response.status_code != 204:
            raise RuntimeError(response.json())

    def authorize_subscription(self, items):
        response = self.talk_to_miau_server('subscription', {'items':items})

        # Raise an error if the server does not reply with 204 (OK, Resource
        # Created)
        if response.status_code != 201:
            raise RuntimeError(response.json())

        # Return just the token
        return response.json()['token']
