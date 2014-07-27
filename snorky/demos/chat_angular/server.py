import os
from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler
from snorky.message_handler import MessageHandler
from snorky.request_handlers.websocket import SnorkyWebSocketHandler

from snorky.services.messaging import MessagingService

# Adapted from http://stackoverflow.com/a/23818878/1777162
class IndexAwareStaticFileHandler(StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path += 'index.html'

        return StaticFileHandler.parse_url_path(self, url_path)

if __name__ == "__main__":
    io_loop = IOLoop.instance()
    message_handler = MessageHandler()
    message_handler.register_service(MessagingService("messaging"))

    dirname = os.path.dirname(__file__)
    application = Application([
        SnorkyWebSocketHandler.get_route(message_handler, "/ws"),
        (r"/(.*)", IndexAwareStaticFileHandler, {"path": dirname}),
    ])
    application.listen(5800)

    try:
        print("Snorky running...")
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
