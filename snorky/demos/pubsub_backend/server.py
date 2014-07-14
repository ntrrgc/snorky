import os
from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler
from snorky.server.message_handler import MessageHandler

from snorky.server.request_handlers.http import BackendHTTPHandler
from snorky.server.request_handlers.websocket import SnorkyWebSocketHandler

from snorky.server.services.pubsub import PubSubService, PubSubBackend

# Adapted from http://stackoverflow.com/a/23818878/1777162
class IndexAwareStaticFileHandler(StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path += 'index.html'

        return StaticFileHandler.parse_url_path(self, url_path)

class PrivatePubSub(PubSubService):
    def can_publish(self, client, channel):
        # Publishing is only allowed from the backend
        return False

if __name__ == "__main__":
    io_loop = IOLoop.instance()
    message_handler = MessageHandler()

    pubsub = PrivatePubSub("pubsub")
    pubsub_backend = PubSubBackend("pubsub_backend", pubsub)
    message_handler.register_service(pubsub)
    message_handler.register_service(pubsub_backend)

    dirname = os.path.dirname(__file__)
    application = Application([
        SnorkyWebSocketHandler.get_route(message_handler, "/ws"),
        (r"/backend", BackendHTTPHandler, {
            "message_handler": message_handler,
            "api_key": "swordfish"
        }),
        (r"/(.*)", IndexAwareStaticFileHandler, {"path": dirname}),
    ])
    application.listen(5800)

    try:
        print("Snorky running...")
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
