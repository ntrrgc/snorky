# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from snorky.services.base import format_call
from snorky.hashable import make_hashable


class TestRequest(object):
    """Mocked Request class for use with RPC services"""

    def __init__(self, service, client, command, params):
        self.service = service
        self.client = client
        self.command = command
        self.params = make_hashable(params)
        self.debug = True # propagate internal errors

        self.call_id = None
        self.resolved = False
        self.response = None
        self.response_type = None

    def reply(self, data):
        if self.resolved:
            raise RuntimeError("This request has already been resolved")

        self.response_type = "response"
        self.response = data
        self.resolved = True

    def error(self, msg):
        if self.resolved:
            raise RuntimeError("This request has already been resolved")

        self.response_type = "error"
        self.response = msg
        self.resolved = True

    def format_call(self):
        return format_call(self.command, self.params)


class RPCTestMixin(object):
    """Useful methods for testing RPC services"""

    def _rpcCallNoAsserts(self, service, client, command, request_debug=True,
                          **params):
        # request_debug=True tells RPCService to propagate internal errors
        # instead of replying with an RPC error.
        request = TestRequest(service, client, command, params)
        request.debug = request_debug
        service.process_request(request)
        return request

    def rpcCall(self, service, client, command, **params):
        request = self._rpcCallNoAsserts(service, client, command, **params)

        self.assertTrue(request.resolved)
        if request.response_type == "error":
            raise AssertionError("Error in RPC call: %s" % request.response)
        self.assertEqual(request.response_type, "response")
        return request.response

    def rpcExpectError(self, service, client, command, **params):
        request = self._rpcCallNoAsserts(service, client, command, **params)

        self.assertTrue(request.resolved)
        self.assertEqual(request.response_type, "error")
        return request.response
