# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
from snorky.client import Client
from datetime import timedelta
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
        self.ping_pong_interval = kwargs.pop('ping_pong_interval', 90) # seconds
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

        if self.ping_pong_interval:
            IOLoop.instance().add_timeout(
                timedelta(seconds=self.ping_pong_interval),
                self.its_ping_time)

    def its_ping_time(self):
        # Still alive?
        if self.ws_connection:
            # Send a ping frame
            self.ping(b'')

            # Repeat
            if self.ping_pong_interval:
                IOLoop.instance().add_timeout(
                    timedelta(seconds=self.ping_pong_interval),
                    self.its_ping_time)

    def on_message(self, message):
        """Called when a message is received."""
        self.service_registry.process_message_raw(self.client, message)

    def on_close(self):
        """Called when the connection finalizes."""
        self.service_registry.client_disconnected(self.client)

    @classmethod
    def get_route(cls, service_registry, path="/", **kwargs):
        """Returns a route to this request handler, suitable for use in
        :py:class:`tornado.web.Application`.
        """
        options = kwargs.copy()
        options['service_registry'] = service_registry
        return (path, cls, options)
