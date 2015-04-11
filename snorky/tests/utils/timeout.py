# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class TestTimeoutHandle(object):
    def __init__(self, factory):
        self.factory = factory
        self.cancelled = False

    def cancel(self):
        if self.cancelled:
            raise RuntimeError("Already cancelled")
        del self.factory.timeouts[self]
        self.cancelled = True


class TestTimeoutFactory(object):
    def __init__(self):
        self.timeouts = {} # handle -> (callback, args, kwargs)

    def call_later(self, delay, callback, *args, **kwargs):
        handle = TestTimeoutHandle(self)
        self.timeouts[handle] = (callback, args, kwargs)
        return handle

    def process_all(self):
        for callback, args, kwargs in self.timeouts.values():
            callback(*args, **kwargs)

        # Clear timeouts
        self.timeouts.clear()

    @property
    def timeouts_pending(self):
        return len(self.timeouts)
