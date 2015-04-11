# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from tornado.websocket import WebSocketHandler
from snorky.client import Client
import json


class WebSocketClient(Client):
    """A WebSocket client."""
    def __init__(self, req_handler):
        super(WebSocketClient, self).__init__()
        self.req_handler = req_handler

    @property
    def remote_address(self):
        """IP address of the client"""
        return self.req_handler.request.remote_ip

    def send(self, msg):
        """Sends a message through the WebSocket channel."""
        self.req_handler.write_message(json.dumps(msg))


class SnorkyWebSocketHandler(WebSocketHandler):
    """Handles WebSocket connections.

    A ``service_registry`` parameter must be specified for instances of this
    request handler.
    """
    def __init__(self, *args, **kwargs):
        self.service_registry = kwargs.pop("service_registry")
        self.client = WebSocketClient(req_handler=self)
        super(SnorkyWebSocketHandler, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        """By default returns true, telling Tornado to allow cross origin
        requests.
        """
        # TODO Allow to customize this
        return True

    def open(self):
        """Executed when the connection is started."""
        self.service_registry.client_connected(self.client)

    def on_message(self, message):
        """Called when a message is received."""
        self.service_registry.process_message_raw(self.client, message)

    def on_close(self):
        """Called when the connection finalizes."""
        self.service_registry.client_disconnected(self.client)

    @classmethod
    def get_route(cls, service_registry, path="/"):
        """Returns a route to this request handler, suitable for use in
        :py:class:`tornado.web.Application`.
        """
        return (path, cls, {'service_registry': service_registry})
