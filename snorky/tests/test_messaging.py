# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from unittest import TestCase
from snorky.types import is_string
from snorky.services.messaging import MessagingService
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
                           "registerParticipant", name="Alice")
        self.assertEqual(data, None)

    def test_register_twice(self):
        # Register Alice first
        self.test_register()

        # Now register Bob
        data = self.rpcCall(self.service, self.bob,
                            "registerParticipant", name="Bob")
        self.assertEqual(data, None)

    def test_register_same_name(self):
        # Register Alice first
        self.test_register()

        # Try to register Alice again
        msg = self.rpcExpectError(self.service, self.alice,
                                  "registerParticipant", name="Alice")
        self.assertEqual(msg, "Name already registered")

    def test_banned_name(self):
        msg = self.rpcExpectError(self.service, self.alice,
                                  "registerParticipant", name="DrDuck")
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
                "dest": "Bob",
                "body": "Hi, Bob."
            }
        })

    def test_register_three(self):
        # Register both Alice and Bob
        self.test_register_twice()

        # Now register Carol
        data = self.rpcCall(self.service, self.carol,
                            "registerParticipant", name="Carol")
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
                            "listParticipants")
        self.assertEqual(data, ["Alice", "Bob", "Carol"])

    def test_unregister_participant(self):
        self.test_register_twice()

        # Bob unregisters
        data = self.rpcCall(self.service, self.bob,
                            "unregisterParticipant", name="Bob")
        self.assertEqual(data, None)

        msg = self.rpcExpectError(self.service, self.alice,
                                  "send", sender="Alice", dest="Bob",
                                  body="You should not receive this")
        self.assertEqual(msg, "Unknown destination")

        data = self.rpcCall(self.service, self.alice,
                            "listParticipants")
        self.assertEqual(data, ["Alice"])

    def test_unregister_unknown_participant(self):
        self.test_register_twice()

        # Bob tries to unregister Allice
        msg = self.rpcExpectError(self.service, self.bob,
                                  "unregisterParticipant", name="Charlie")
        self.assertEqual(msg, "Unknown participant")

    def test_unregister_other_participant(self):
        self.test_register_twice()

        # Bob tries to unregister Allice
        msg = self.rpcExpectError(self.service, self.bob,
                                  "unregisterParticipant", name="Alice")
        self.assertEqual(msg, "Invalid participant")

        data = self.rpcCall(self.service, self.alice,
                            "listParticipants")
        self.assertEqual(data, ["Alice", "Bob"])

    def test_disconnect(self):
        self.test_register()

        self.assertIn("Alice", self.service.participants)
        self.assertIn(self.alice, self.service.client_participants)

        self.service.client_disconnected(self.alice)

        self.assertNotIn("Alice", self.service.participants)
        self.assertNotIn(self.alice, self.service.client_participants)

    def test_disconnect_unknown(self):
        # Alice is not registered

        self.assertNotIn("Alice", self.service.participants)
        self.assertNotIn(self.alice, self.service.client_participants)

        self.service.client_disconnected(self.alice)
        # No errors


if __name__ == "__main__":
    unittest.main()
