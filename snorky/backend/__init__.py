# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests
import json
import logging

log = logging.getLogger('snorky')
websession = requests.session()

class SnorkyError(Exception):
    """An error triggered by the Snorky RPC system."""
    pass

class SnorkyHTTPTransport(object):
    """Defines how messages are sent to Snorky."""
    def __init__(self, url, key):
        self.url = url
        self.key = key

    def send(self, message, json=json):
        """Sends a message to Snorky service, encoded in JSON with the
        library provided in the optional ``json`` argument (by default it will
        use the default :mod:`json` module).
        """
        response = websession.post(self.url, headers={
            "X-Backend-Key": self.key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }, data=json.dumps(message).encode("UTF-8"))

        if not response.ok:
            raise RuntimeError("Error from Snorky server: %d %s" %
                               (response.status_code, response.reason))

        try:
            response = json.loads(response.content.decode("UTF-8"))
        except ValueError:
            raise RuntimeError("Non-JSON response from Snorky: %s" %
                               response.content)

        return response


class SnorkyBackend(object):
    """Provides methods to send messanges and make calls against Snorky RPC
    services."""
    def __init__(self, transport, json=json):
        self.transport = transport
        self.json = json

    def send(self, message):
        """Send a bare message to Snorky."""
        return self.transport.send(message, json=self.json)

    def call(self, service, command, **params):
        """Make an RPC call to a Snorky service.

        Returns the returned value of the RPC call."""
        log.debug("Service: %s, Call: %s %s", service, command, params)
        response = self.send({
            "service": service,
            "message": {
                "command": command,
                "params": params
            }
        })

        # We're only interested in the response from the service
        response = response["message"]

        if response["type"] == "response":
            log.debug("Response: %s", response["data"])
            return response["data"]
        elif response["type"] == "error":
            log.debug("Error: %s", response["message"])
            raise SnorkyError(response["message"])
        else:
            raise RuntimeError
