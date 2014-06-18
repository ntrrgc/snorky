from unittest import TestCase
from miau.common.types import is_string
from snorky.server.services.messaging import MessagingService
from snorky.tests.utils.rpc import RPCTestMixin


class MockClient(object):
    def __init__(self, test, msg_prop):
        self.test = test
        self.msg_prop = msg_prop

    def send(self, msg):
        setattr(self.test, self.msg_prop, msg)


class TestMessagingService(MessagingService):
    def is_name_allowed(self, client, name):
        return is_string(name) and "duck" not in name.lower()


class TestMessaging(RPCTestMixin, TestCase):
    def setUp(self):
        self.service = TestMessagingService("messaging")
        self.msg_alice = None
        self.msg_bob = None
        self.msg_carol = None
        self.alice = MockClient(self, "msg_alice")
        self.bob = MockClient(self, "msg_bob")
        self.carol = MockClient(self, "msg_carol")

    def test_register(self):
        data = self.rpcCall(self.service, self.alice,
                           "register_participant", name="Alice")
        self.assertEqual(data, None)

    def test_register_twice(self):
        # Register Alice first
        self.test_register()

        # Now register Bob
        data = self.rpcCall(self.service, self.bob,
                            "register_participant", name="Bob")
        self.assertEqual(data, None)

    def test_register_same_name(self):
        # Register Alice first
        self.test_register()

        # Try to register Alice again
        msg = self.rpcExpectError(self.service, self.alice,
                                  "register_participant", name="Alice")
        self.assertEqual(msg, "Name already registered")

    def test_banned_name(self):
        msg = self.rpcExpectError(self.service, self.alice,
                                  "register_participant", name="DrDuck")
        self.assertEqual(msg, "Name not allowed")

    def test_send(self):
        # Register both Alice and Bob
        self.test_register_twice()

        # Alice sends a message to Bob
        data = self.rpcCall(self.service, self.alice,
                            "send", sender="Alice", dest="Bob",
                            body="Hi, Bob.")
        # Alice gets send confirmation
        self.assertEqual(data, None)

        # Bob has received the message
        self.assertEqual(self.msg_bob, {
            "service": "messaging",
            "message": {
                "type": "message",
                "sender": "Alice",
                "body": "Hi, Bob."
            }
        })

    def test_register_three(self):
        # Register both Alice and Bob
        self.test_register_twice()

        # Now register Carol
        data = self.rpcCall(self.service, self.carol,
                            "register_participant", name="Carol")
        self.assertEqual(data, None)

    def test_send_forgery(self):
        # Register Alice, Bob and Carol
        self.test_register_twice()

        # Alice tries to send a message to Bob, pretending to be Carol
        self.msg_bob = None
        msg = self.rpcExpectError(self.service, self.alice,
                                  "send", sender="Carol", dest="Bob",
                                  body="Hi, Bob.")
        self.assertEqual(msg, "Invalid sender")

        # Bob has not received anything
        self.assertIsNone(self.msg_bob)

    def test_send_non_existing_sender(self):
        # Register Alice, Bob and Carol
        self.test_register_twice()

        # Alice tries to send a message to Bob with invalid sender
        self.msg_bob = None
        msg = self.rpcExpectError(self.service, self.alice,
                                  "send", sender="Charlie", dest="Bob",
                                  body="Hi, Bob")
        self.assertEqual(msg, "Invalid sender")

        # Bob has not received anything
        self.assertIsNone(self.msg_bob)

    def test_send_non_existing_recipient(self):
        self.test_register_twice()

        msg = self.rpcExpectError(self.service, self.alice,
                                  "send", sender="Alice", dest="Charlie",
                                  body="Hi, Charlie")
        self.assertEqual(msg, "Unknown destination")

    def test_list_participants(self):
        self.test_register_three()

        data = self.rpcCall(self.service, self.alice,
                            "list_participants")
        self.assertEqual(data, ["Alice", "Bob", "Carol"])

if __name__ == "__main__":
    unittest.main()
