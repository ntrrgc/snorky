# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from tornado.ioloop import IOLoop


class TornadoTimeoutHandle(object):
    """Represents a handle to a Tornado timeout."""
    def __init__(self, io_loop, tornado_handle):
        self.io_loop = io_loop
        self.tornado_handle = tornado_handle
        self.cancelled = False

    def cancel(self):
        """Cancels the timeout."""
        if self.cancelled:
            raise RuntimeError("Already cancelled")
        self.io_loop.remove_timeout(self.tornado_handle)
        self.cancelled = True


class _TornadoTimeoutFactory(object):
    """Factory class to create timeout handle objects."""
    def __init__(self, io_loop=None):
        self.io_loop = io_loop or IOLoop.instance()

    def call_later(self, delay, callback, *args, **kwargs):
        """Returns an instance of :class:`TornadoTimeoutHandle` associated with
        a Tornado timeout which will execute the provided callback with
        provided arguments in the specified delay in seconds, starting to count
        from now.
        """
        time = self.io_loop.time() + delay
        handle = self.io_loop.call_at(time, callback, *args, **kwargs)
        assert handle is not None
        return TornadoTimeoutHandle(self.io_loop, handle)


TornadoTimeoutFactory = _TornadoTimeoutFactory()
