from __future__ import absolute_import
from miau.server.frontend import FrontendHandler
from sockjs.tornado import SockJSRouter, SockJSConnection
from tornado.web import Application


class FrontendSockJSHandler(FrontendHandler, SockJSConnection):
    def on_open(self, info):
        FrontendHandler.open(self)

    def write_message(self, message):
        SockJSConnection.send(self, message)


class SockJSFrontend(Application):
    def __init__(self, facade):
        # Since SockJS does not provide (AFAIK) a mechanism to pass arguments
        # to the SockJSConnection constructor, set the facade using an ad-hoc
        # subclass instead.
        class ThisFacadeSockJSHandler(FrontendSockJSHandler):
            def __init__(self, *args, **kwargs):
                FrontendHandler.__init__(self, facade)
                SockJSConnection.__init__(self, *args, **kwargs)


        sockjs_router = SockJSRouter(ThisFacadeSockJSHandler, '')
        super(SockJSFrontend, self).__init__(sockjs_router.urls)
