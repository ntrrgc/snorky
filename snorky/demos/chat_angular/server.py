import os
from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler
from snorky.server.message_handler import MessageHandler
from snorky.server.request_handlers.websocket import SnorkyWebSocketHandler

from snorky.server.services.messaging import MessagingService

if __name__ == "__main__":
    io_loop = IOLoop.instance()
    message_handler = MessageHandler()
    message_handler.register_service(MessagingService("messaging"))

    dirname = os.path.dirname(__file__)
    application = Application([
        SnorkyWebSocketHandler.get_route(message_handler, "/ws"),
        (r"/(.*)", StaticFileHandler, {"path": dirname}),
    ])
    application.listen(5800)

    try:
        print("Snorky running...")
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
