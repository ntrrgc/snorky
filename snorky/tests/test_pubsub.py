from snorky.server.services.pubsub import PubSubService, PubSubBackend

from snorky.tests.utils.rpc import RPCTestMixin
from unittest import TestCase
import unittest


class MyPubSub(PubSubService):
    def can_publish(self, client, channel):
        # The "operators" channel is restricted
        return channel != "operators"


class MockClient(object):
    def __init__(self, test, msg_prop):
        self.test = test
        self.msg_prop = msg_prop

    def send(self, msg):
        setattr(self.test, self.msg_prop, msg)


class TestPubSub(RPCTestMixin, TestCase):
    def setUp(self):
        self.service = MyPubSub("pubsub")

        self.alice = MockClient(self, "msg_alice")
        self.bob = MockClient(self, "msg_bob")

    def test_send(self):
        data = self.rpcCall(self.service, self.alice,
                            "subscribe", channel="offtopic")
        self.assertEqual(data, None)

        data = self.rpcCall(self.service, self.bob,
                            "publish", channel="offtopic", message="Hello")
        self.assertEqual(data, None)

        self.assertEqual(self.msg_alice, {
            "service": "pubsub",
            "message": {
                "type": "message",
                "channel": "offtopic",
                "message": "Hello"
            },
        })

    def test_unsubscribe(self):
        self.test_send()

        data = self.rpcCall(self.service, self.alice,
                            "unsubscribe", channel="offtopic")
        self.assertEqual(data, None)
        self.msg_alice = None

        # Send a message to the unsubscripted channel
        data = self.rpcCall(self.service, self.bob,
                            "publish", channel="offtopic", message="Hello")
        self.assertEqual(data, None)

        # Alice has not received anything
        self.assertIsNone(self.msg_alice)

    def test_send_empty(self):
        data = self.rpcCall(self.service, self.alice,
                            "publish", channel="offtopic", message="Hello")
        self.assertEqual(data, None)

        # No errors, no exceptions

    def test_send_restricted(self):
        msg = self.rpcExpectError(self.service, self.alice,
                                  "publish", channel="operators",
                                  message="Hello")
        self.assertEqual(msg, "Not authorized")

    def test_backend(self):
        data = self.rpcCall(self.service, self.alice,
                            "subscribe", channel="operators")
        self.assertEqual(data, None)

        backend = PubSubBackend("pubsub_backend", self.service)
        data = self.rpcCall(backend, None,
                            "publish", channel="operators",
                            message="Hi from operators")
        self.assertEqual(data, None)

        self.assertEqual(self.msg_alice, {
            "service": "pubsub",
            "message": {
                "type": "message",
                "channel": "operators",
                "message": "Hi from operators"
            },
        })


if __name__ == "__main__":
    unittest.main()
