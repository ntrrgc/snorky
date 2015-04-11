# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from snorky.service_registry import ServiceRegistry
from snorky.services.base import Service
from snorky.client import Client
from tornado.testing import ExpectLog

import unittest


class EchoService(Service):
    def process_message_from(self, client, msg):
        # Messages received should be hashable
        hash(msg)

        self.send_message_to(client, msg)


class MockClient(Client):
    def __init__(self, test):
        self.test = test

    def send(self, msg):
        self.test.msg = msg


class TestServiceRegistry(unittest.TestCase):
    def setUp(self):
        self.client = MockClient(self)
        self.mh = ServiceRegistry()
        self.mh.register_service(EchoService("echo"))
        self.msg = None

    def test_initialize_with_services(self):
        self.mh = ServiceRegistry([EchoService("echo")])

        self.test_call()

    def test_call(self):
        self.mh.process_message_from(self.client, {
            "service": "echo",
            "message": "foo"
        })
        self.assertEqual(self.msg, {
            "service": "echo",
            "message": "foo"
        })

    def test_process_message_raw_complex(self):
        self.mh.process_message_raw(self.client, '''{
            "service": "echo",
            "message": { "favoriteNumbers": [3, 5, 0] }
        }''')
        self.assertEqual(self.msg, {
            "service": "echo",
            "message": { "favoriteNumbers": [3, 5, 0] }
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
        with ExpectLog("snorky", 'Invalid JSON.*'):
            self.mh.process_message_raw(self.client, '''{
                "service": "echo''')

    def test_bad_service(self):
        with ExpectLog("snorky",
                       'Message for non existing service "bar" from client'):
            self.mh.process_message_from(self.client, {
                "service": "bar",
                "message": "foo"
            })

    def test_bad_package(self):
        with ExpectLog("snorky",
                       'Malformed message from client'):
            self.mh.process_message_from(self.client, {"cat": 42})


if __name__ == "__main__":
    unittest.main()
