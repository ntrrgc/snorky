from sockjs.tornado import SockJSRouter, SockJSConnection
from snorky.client import Client
import json


class SockJSClient(Client):
    def __init__(self, req_handler):
        super(SockJSClient, self).__init__()
        self.req_handler = req_handler

    @property
    def remote_address(self):
        return self.req_handler.request.remote_ip

    def send(self, msg):
        self.req_handler.send(json.dumps(msg))


class SnorkySockJSHandler(SockJSConnection):
    def __init__(self, service_registry, *args, **kwargs):
        self.service_registry = service_registry
        self.client = SockJSClient(req_handler=self)

        SockJSConnection.__init__(self, *args, **kwargs)

    def on_open(self, info):
        self.service_registry.client_connected(self.client)

    def on_message(self, message):
        self.service_registry.process_message_raw(self.client, message)

    def on_close(self):
        self.service_registry.client_disconnected(self.client)

    @classmethod
    def get_routes(cls, service_registry, path=""):
        # Since SockJS does not provide (AFAIK) a mechanism to pass arguments
        # to the SockJSConnection constructor, we use an ad-hoc subclass
        class ThisSockJSHandler(cls):
            def __init__(self, *args, **kwargs):
                cls.__init__(self, service_registry, *args, **kwargs)

        return SockJSRouter(ThisSockJSHandler, path).urls
