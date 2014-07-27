from tornado.ioloop import IOLoop
from tornado.web import Application
from snorky.message_handler import MessageHandler
from snorky.request_handlers.websocket import SnorkyWebSocketHandler

from snorky.services.base import RPCService, allowed_command


class FooService(RPCService):
    @allowed_command
    def sum(self, req, a, b):
        return a + b


if __name__ == "__main__":
    io_loop = IOLoop.instance()
    message_handler = MessageHandler()
    message_handler.register_service(FooService("calc"))

    application = Application([
        SnorkyWebSocketHandler.get_route(message_handler)
    ])
    application.listen(8000)

    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
