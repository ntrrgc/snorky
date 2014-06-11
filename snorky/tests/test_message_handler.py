from snorky.server.message_handler import MessageHandler
from snorky.server.services.base import Service
from snorky.server.client import Client
from tornado.testing import ExpectLog

import unittest


class EchoService(Service):
    def process_message_from(self, client, msg):
        self.send_message_to(client, msg)


class MockClient(Client):
    def __init__(self, test):
        self.test = test

    def send(self, msg):
        self.test.msg = msg


class TestMessageHandler(unittest.TestCase):
    def setUp(self):
        self.client = MockClient(self)
        self.mh = MessageHandler()
        self.mh.register_service(EchoService("echo"))
        self.msg = None

    def test_call(self):
        self.mh.process_message_from(self.client, {
            "service": "echo",
            "message": "foo"
        })
        self.assertEqual(self.msg, {
            "service": "echo",
            "message": "foo"
        })

    def test_process_message_raw(self):
        self.mh.process_message_raw(self.client, '''{
            "service": "echo",
            "message": "foo"
        }''')
        self.assertEqual(self.msg, {
            "service": "echo",
            "message": "foo"
        })

    def test_invalid_json(self):
        with ExpectLog("tornado.general", 'Invalid JSON.*'):
            self.mh.process_message_raw(self.client, '''{
                "service": "echo''')

    def test_bad_service(self):
        with ExpectLog("tornado.general",
                       'Message for non existing service "bar" from client'):
            self.mh.process_message_from(self.client, {
                "service": "bar",
                "message": "foo"
            })

    def test_bad_package(self):
        with ExpectLog("tornado.general",
                       'Malformed message from client'):
            self.mh.process_message_from(self.client, {"cat": 42})


if __name__ == "__main__":
    unittest.main()
