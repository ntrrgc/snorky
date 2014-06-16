from snorky.server.services.base import format_call


class TestRequest(object):
    def __init__(self, service, client, command, params):
        self.service = service
        self.client = client
        self.command = command
        self.params = params

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
    def _rpcCallNoAsserts(self, service, client, command, **params):
        request = TestRequest(service, client, command, params)
        service.process_request(request)
        return request

    def rpcCall(self, service, client, command, **params):
        request = self._rpcCallNoAsserts(service, client, command, **params)

        self.assertTrue(request.resolved)
        self.assertEqual(request.response_type, "response")
        return request.response

    def rpcExpectError(self, service, client, command, **params):
        request = self._rpcCallNoAsserts(service, client, command, **params)

        self.assertTrue(request.resolved)
        self.assertEqual(request.response_type, "error")
        return request.response


