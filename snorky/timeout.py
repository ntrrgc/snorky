from tornado.ioloop import IOLoop


class TornadoTimeoutHandle(object):
    def __init__(self, io_loop, tornado_handle):
        self.io_loop = io_loop
        self.tornado_handle = tornado_handle
        self.cancelled = False

    def cancel(self):
        if self.cancelled:
            raise RuntimeError("Already cancelled")
        self.io_loop.remove_timeout(self.tornado_handle)
        self.cancelled = True


class _TornadoTimeoutFactory(object):
    def __init__(self, io_loop=None):
        self.io_loop = io_loop or IOLoop.instance()

    def call_later(self, delay, callback, *args, **kwargs):
        time = self.io_loop.time() + delay
        handle = self.io_loop.call_at(time, callback, *args, **kwargs)
        assert handle is not None
        return TornadoTimeoutHandle(self.io_loop, handle)


TornadoTimeoutFactory = _TornadoTimeoutFactory()
