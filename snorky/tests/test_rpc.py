# -*- encoding: UTF-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from snorky.client import Client
from snorky.services.base import RPCService, RPCError, format_call
from snorky.tests.utils.rpc import RPCTestMixin
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


class TestRPC(RPCTestMixin, TestCase):
    def setUp(self):
        self.client = MockClient(self)
        self.calculator = CalculatorService("calc")
        self.msg = None

    def test_process_message(self):
        self.calculator.process_message_from(self.client, {
            "command": "sum",
            "callId": 1,
            "params": {
                "a": 5,
                "b": 12,
            },
        })
        self.assertEqual(self.msg, {
            "service": "calc",
            "message": {
                "type": "response",
                "callId": 1,
                "data": 17,
            },
        })

    def test_message_without_call_id(self):
        self.calculator.process_message_from(self.client, {
            "command": "sum",
            "params": {
                "a": 5,
                "b": 12,
            },
        })
        self.assertEqual(self.msg, {
            "service": "calc",
            "message": {
                "type": "response",
                "data": 17,
            },
        })

    def test_call_return(self):
        data = self.rpcCall(self.calculator, self.client,
                            "sum", a=5, b=12)
        self.assertEqual(data, 17)

    def test_call_request(self):
        data = self.rpcCall(self.calculator, self.client,
                            "difference", a=5, b=12)
        self.assertEqual(data, -7)

    def test_unknown_command(self):
        msg = self.rpcExpectError(self.calculator, self.client,
                                  "foo")
        self.assertEqual(msg, "Unknown command")

    def test_bad_message(self):
        with ExpectLog("snorky",
                       'Invalid format in RPC service "calc". Message: .*'):
            self.calculator.process_message_from(self.client, {
                "command": "",
            })

        self.assertIsNone(self.msg)

    def test_invalid_params(self):
        with ExpectLog("snorky",
                       'Invalid params in RPC service "calc": '
                       'difference\(\{"a": 5\}\)'):
            msg = self.rpcExpectError(self.calculator, self.client,
                                      "difference", a=5)
            self.assertEqual(msg, "Invalid params")

    def test_internal_error(self):
        with ExpectLog("snorky",
                       'Unhandled exception in RPC service .*'):
            self.calculator.process_message_from(self.client, {
                "command": "buggy",
                "callId": 3,
                "params": {}
            })
            self.assertEqual(self.msg, {
                "service": "calc",
                "message": {
                    "type": "error",
                    "callId": 3,
                    "message": "Internal error"
                }
            })

    def test_internal_type_error(self):
        with ExpectLog("snorky",
                       'Unhandled exception in RPC service .*'):
            msg = self.rpcExpectError(self.calculator, self.client,
                                      "buggy_type_error", request_debug=False)
            self.assertEqual(msg, "Internal error")


if __name__ == "__main__":
    unittest.main()
