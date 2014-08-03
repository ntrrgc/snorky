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
        self.message_handler = kwargs.pop("message_handler")
        self.client = WebSocketClient(req_handler=self)
        super(SnorkyWebSocketHandler, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        # TODO Allow to customize this
        return True

    def open(self):
        self.message_handler.client_connected(self.client)

    def on_message(self, message):
        self.message_handler.process_message_raw(self.client, message)

    def on_close(self):
        self.message_handler.client_disconnected(self.client)

    @classmethod
    def get_route(cls, message_handler, path="/"):
        return (path, cls, {'message_handler': message_handler})
