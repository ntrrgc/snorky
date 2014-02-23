import tornado.ioloop
from miau.server.managers.subscription import SubscriptionManager
from miau.server.managers.dealer import DealerManager
from miau.server.facade import Facade
from miau.server.frontend import Frontend
from miau.server.backend import Backend

if __name__ == "__main__":
    dm = DealerManager()
    sm = SubscriptionManager()
    io_loop = tornado.ioloop.IOLoop.instance()
    facade = Facade(dm, sm, io_loop)

    backend = Backend(facade)
    frontend = Frontend(facade)

    backend.listen(7123)
    frontend.listen(8001)

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
