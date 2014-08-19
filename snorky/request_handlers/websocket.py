from tornado.websocket import WebSocketHandler
from snorky.client import Client
import json


class WebSocketClient(Client):
    def __init__(self, req_handler):
        super(WebSocketClient, self).__init__()
        self.req_handler = req_handler

    @property
    def remote_address(self):
        return self.req_handler.request.remote_ip

    def send(self, msg):
        self.req_handler.write_message(json.dumps(msg))


class SnorkyWebSocketHandler(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.service_registry = kwargs.pop("service_registry")
        self.client = WebSocketClient(req_handler=self)
        super(SnorkyWebSocketHandler, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        # TODO Allow to customize this
        return True

    def open(self):
        self.service_registry.client_connected(self.client)

    def on_message(self, message):
        self.service_registry.process_message_raw(self.client, message)

    def on_close(self):
        self.service_registry.client_disconnected(self.client)

    @classmethod
    def get_route(cls, service_registry, path="/"):
        return (path, cls, {'service_registry': service_registry})
