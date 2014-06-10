from snorky.server.client import Client
from snorky.server.services.base import RPCService, allowed_command, RPCMeta
import unittest


class MockClient(Client):
    def __init__(self, test):
        self.test = test

    def send(self, msg):
        self.test.msg = msg


class CalculatorService(RPCService):
    @allowed_command
    def sum(self, req, a, b):
        return a + b


class CalculatorExtendedService(CalculatorService):
    @allowed_command
    def difference(self, req, a, b):
        return a - b


class TestRPC(unittest.TestCase):
    def setUp(self):
        self.client = MockClient(self)
        self.msg = None
        self.calculator = CalculatorService("calc")
        self.calculator_ex = CalculatorExtendedService("calc_ex")

    def test_allowed_commands(self):
        self.assertEqual(self.calculator.allowed_commands, {"sum"})
        self.assertEqual(self.calculator_ex.allowed_commands,
                         {"sum", "difference"})

    def test_base_existent(self):
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

    def test_base_not_existent(self):
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
                "type": "error",
                "call_id": 1,
                "message": "Unknown command",
            },
        })

    def test_extended_old_command(self):
        self.calculator_ex.process_message_from(self.client, {
            "command": "sum",
            "call_id": 1,
            "params": {
                "a": 5,
                "b": 12,
            },
        })
        self.assertEqual(self.msg, {
            "service": "calc_ex",
            "message": {
                "type": "response",
                "call_id": 1,
                "data": 17,
            },
        })

    def test_extended_new_command(self):
        self.calculator_ex.process_message_from(self.client, {
            "command": "difference",
            "call_id": 1,
            "params": {
                "a": 5,
                "b": 12,
            },
        })
        self.assertEqual(self.msg, {
            "service": "calc_ex",
            "message": {
                "type": "response",
                "call_id": 1,
                "data": -7,
            },
        })


if __name__ == "__main__":
    unittest.main()
