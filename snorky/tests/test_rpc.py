from snorky.server.client import Client
from snorky.server.services.base import RPCService, RPCError
from tornado.testing import ExpectLog
import unittest


class MockClient(Client):
    def __init__(self, test):
        self.test = test

    def send(self, msg):
        self.test.msg = msg


class CalculatorService(RPCService):
    rpc_commands = {"sum", "difference", "buggy", "buggy_type_error"}

    def sum(self, req, a, b):
        return a + b

    def difference(self, req, a, b):
        req.reply(a - b)

    def buggy(self, req):
        raise RuntimeError("Snap! I crashed :(")

    def buggy_type_error(self, req):
        raise TypeError


class TestRPC(unittest.TestCase):
    def setUp(self):
        self.client = MockClient(self)
        self.calculator = CalculatorService("calc")
        self.msg = None

    def test_call_return(self):
        self.calculator.process_message_from(self.client, {
            "command": "sum",
            "call_id": 1,
            "params": {
                "a": 5,
                "b": 12,
            },
        })
        self.assertEqual(self.msg, {
            "service": "calc",
            "message": {
                "type": "response",
                "call_id": 1,
                "data": 17,
            },
        })

    def test_call_request(self):
        self.calculator.process_message_from(self.client, {
            "command": "difference",
            "call_id": 1,
            "params": {
                "a": 5,
                "b": 12,
            },
        })
        self.assertEqual(self.msg, {
            "service": "calc",
            "message": {
                "type": "response",
                "call_id": 1,
                "data": -7,
            },
        })

    def test_unknown_command(self):
        self.calculator.process_message_from(self.client, {
            "command": "foo",
            "call_id": 2,
            "params": {},
        })
        self.assertEqual(self.msg, {
            "service": "calc",
            "message": {
                "type": "error",
                "call_id": 2,
                "message": "Unknown command",
            }
        })

    def test_bad_message(self):
        with ExpectLog("tornado.general",
                       'Invalid format in RPC service "calc". Message: .*'):
            self.calculator.process_message_from(self.client, {
                "command": "",
            })

        self.assertIsNone(self.msg)

    def test_invalid_params(self):
        with ExpectLog("tornado.general",
                       'Invalid params in RPC service "calc". Message: .*'):
            self.calculator.process_message_from(self.client, {
                "command": "difference",
                "call_id": 1,
                "params": {
                    "a": 5,
                },
            })

        self.assertEqual(self.msg, {
            "service": "calc",
            "message": {
                "type": "error",
                "call_id": 1,
                "message": "Invalid params"
            },
        })

    def test_internal_error(self):
        with ExpectLog("tornado.general",
                       'Unhandled exception in RPC service .*'):
            self.calculator.process_message_from(self.client, {
                "command": "buggy",
                "call_id": 3,
                "params": {}
            })
            self.assertEqual(self.msg, {
                "service": "calc",
                "message": {
                    "type": "error",
                    "call_id": 3,
                    "message": "Internal error"
                }
            })

    def test_internal_type_error(self):
        with ExpectLog("tornado.general",
                       'Unhandled exception in RPC service .*'):
            self.calculator.process_message_from(self.client, {
                "command": "buggy_type_error",
                "call_id": 3,
                "params": {}
            })
            self.assertEqual(self.msg, {
                "service": "calc",
                "message": {
                    "type": "error",
                    "call_id": 3,
                    "message": "Internal error"
                }
            })


if __name__ == "__main__":
    unittest.main()
