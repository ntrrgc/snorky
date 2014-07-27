from tornado.web import RequestHandler, HTTPError, asynchronous
from snorky.client import Client
from hmac import compare_digest
import json


class HTTPClient(Client):
    def __init__(self, req_handler):
        super(HTTPClient, self).__init__()
        self.req_handler = req_handler

    @property
    def remote_address(self):
        return self.req_handler.request.remote_ip

    def send(self, msg):
        self.req_handler.write(msg)
        self.req_handler.finish()


class BackendHTTPHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        self.api_key = kwargs.pop("api_key")
        self.message_handler = kwargs.pop("message_handler")
        self.client = HTTPClient(self)
        super(BackendHTTPHandler, self).__init__(*args, **kwargs)

    @asynchronous
    def post(self):
        # Raises HTTP error if wrong key
        self.check_api_key()

        try:
            msg = json.loads(self.request.body.decode("UTF-8"))
        except ValueError:
            raise HTTPError(400, "Invalid JSON")

        self.message_handler.process_message_from(self.client, msg)

    def check_api_key(self):
        try:
            key = self.request.headers["X-Backend-Key"]
        except KeyError:
            raise HTTPError(401, "Missing X-Backend-Key header")

        if not compare_digest(key, self.api_key):
            raise HTTPError(401, "Invalid API key")
