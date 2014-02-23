from miau.server.frontend import FrontendHandler
from tornado.websocket import WebSocketHandler
from tornado.web import Application


class FrontendWebSocketHandler(FrontendHandler, WebSocketHandler):
    def __init__(self, application, request, facade, *args, **kwargs):
        FrontendHandler.__init__(self, facade)
        WebSocketHandler.__init__(self, application, request, *args, **kwargs)


class WebSocketFrontend(Application):
    def __init__(self, facade):
        super(WebSocketFrontend, self).__init__([
            (r"/", FrontendWebSocketHandler, {'facade': facade}),
        ])
