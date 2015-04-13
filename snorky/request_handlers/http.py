# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from tornado.web import RequestHandler, HTTPError, asynchronous
from snorky.client import Client
from streql import equals # constant time string comparison
import json


class HTTPClient(Client):
    """An HTTP client."""
    def __init__(self, req_handler):
        super(HTTPClient, self).__init__()
        self.req_handler = req_handler

    @property
    def remote_address(self):
        """IP address of the client"""
        return self.req_handler.request.remote_ip

    def send(self, msg):
        """Sends a message on the HTTP response."""
        self.req_handler.write(msg)
        self.req_handler.finish()


class BackendHTTPHandler(RequestHandler):
    """A Snorky request handler working over the HTTP protocol.

    This class is intended only for backend use:

     * Only two messages may be exchanged: a request and a response.
     * No ``client_connected`` or ``client_disconnected`` events are
       dispatched.
     """
    def __init__(self, *args, **kwargs):
        self.api_key = kwargs.pop("api_key")
        self.service_registry = kwargs.pop("service_registry")
        self.client = HTTPClient(self)
        super(BackendHTTPHandler, self).__init__(*args, **kwargs)

    @asynchronous
    def post(self):
        """Processes a message, which should be encoded as JSON in UTF-8
        inside the request body.

        Prior to the message processing the authentication method
        :py:meth:`check_api_key` is called.
        """

        # Raises HTTP error if wrong key
        self.check_api_key()

        try:
            msg = json.loads(self.request.body.decode("UTF-8"))
        except ValueError:
            raise HTTPError(400, "Invalid JSON")

        # TODO Close request on error
        self.service_registry.process_message_from(self.client, msg)

    def check_api_key(self):
        """Checks whether the requester client has successfully proved its
        identity.

        By default this check consists on comparing the
        ``X-Backend-Key`` request header value with the key stablished in
        :py:attr:`api_key` when this object is created.
        """
        try:
            key = self.request.headers["X-Backend-Key"]
        except KeyError:
            raise HTTPError(401, "Missing X-Backend-Key header")

        if not equals(key, self.api_key):
            raise HTTPError(401, "Invalid API key")
