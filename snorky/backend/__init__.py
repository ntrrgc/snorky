import requests
import json

websession = requests.session()

class SnorkyError(Exception):
    pass

class SnorkyHTTPTransport(object):
    def __init__(self, url, key):
        self.url = url
        self.key = key

    def send(self, message, json=json):
        response = websession.post(self.url, headers={
            "X-Backend-Key": self.key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }, data=json.dumps(message))

        if not response.ok:
            raise RuntimeError("Error from Snorky server: %d %s" %
                               (response.status_code, response.reason))

        try:
            response = json.loads(response.content)
        except ValueError:
            raise RuntimeError("Non-JSON response from Snorky: %s" %
                               response.content)

        return response


class SnorkyBackend(object):
    def __init__(self, transport, json=json):
        self.transport = transport
        self.json = json

    def send(self, message):
        return self.transport.send(message, json=self.json)


    def call(self, service, command, **params):
        response = self.send({
            "service": service,
            "message": {
                "command": command,
                "params": params
            }
        })

        # We"re only interested in the response from the service
        response = response["message"]

        if response["type"] == "response":
            return response["data"]
        elif response["type"] == "error":
            raise SnorkyError(response["message"])
        else:
            raise RuntimeError
