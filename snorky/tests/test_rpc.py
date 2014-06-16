# -*- encoding: UTF-8 -*-
from snorky.server.client import Client
from snorky.server.services.base import RPCService, RPCError, format_call
from tornado.testing import ExpectLog
from unittest import TestCase


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


class TestFormatCall(TestCase):
    def test_call(self):
        self.assertEqual(format_call("sum", {"a": 1, "b": 2}),
                         'sum({"a": 1, "b": 2})')

    def test_strings(self):
        self.assertEqual(format_call("length", {"string": "my cat"}),
                         'length({"string": "my cat"})')

    def test_unicode(self):
        self.assertEqual(format_call("length", {"string": u"ñu"}),
                         u'length({"string": "ñu"})')

    def test_none(self):
        self.assertEqual(format_call("length", {"string": None}),
                         'length({"string": null})')

    def test_multiline(self):
        self.assertEqual(format_call("length", {"string": "a\nb"}),
                         'length({"string": "a\\nb"})')

    def test_ellipsis(self):
        long_string = "a" * 200
        formatted = format_call("length", {"string": long_string})
        self.assertEqual(len(formatted), 100)
        self.assertTrue(formatted.endswith("..."))


class TestRPC(TestCase):
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
                       'Invalid params in RPC service "calc": '
                       'difference\(\{"a": 5\}\)'):
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
