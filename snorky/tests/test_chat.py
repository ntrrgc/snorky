from snorky.services.chat import ChatService

from mock import Mock
from snorky.tests.utils.rpc import RPCTestMixin
from unittest import TestCase
import unittest


class MockClient(object):
    def __init__(self, identity):
        self.identity = identity
        self.send = Mock()


class TestChatService(ChatService):
    def get_time(self):
        return "fake"


class TestChat(RPCTestMixin, unittest.TestCase):
    def setUp(self):
        self.alice = MockClient("Alice")
        self.bob = MockClient("Bob")
        self.charlie = MockClient("Charlie")

        self.service = TestChatService("chat")

    def test_real_get_time_does_not_crash(self):
        ChatService("foo").get_time()

    def assertMembersEqual(self, response, expected_members):
        self.assertEqual(sorted(response["members"]),
                         sorted(expected_members))

    def assertPresence(self, client, identity, status, channel="#cats"):
        client.send.assert_called_once_with({
            "service": "chat",
            "message": {
                "type": "presence",
                "from": identity,
                "status": status,
                "channel": channel,
                "timestamp": "fake",
            }
        })
        client.send.reset_mock()

    def assertNoPresence(self, client):
        self.assertFalse(client.send.called)

    def assertMessage(self, client, identity, body, channel="#cats"):
        client.send.assert_called_once_with({
            "service": "chat",
            "message": {
                "type": "message",
                "from": identity,
                "channel": channel,
                "body": body,
                "timestamp": "fake",
            }
        })
        client.send.reset_mock()

    def assertNoMessage(self, client):
        self.assertFalse(client.send.called)

    def test_join_empty(self):
        response = self.rpcCall(self.service, self.alice,
                                "join", channel="#cats")
        self.assertMembersEqual(response, ["Alice"])
        self.assertNoPresence(self.alice)

    def test_join_two(self):
        self.test_join_empty()

        response = self.rpcCall(self.service, self.bob,
                                "join", channel="#cats")
        self.assertMembersEqual(response, ["Alice", "Bob"])

        # Alice must have received a presence
        self.assertPresence(self.alice, "Bob", "joined")
        self.assertNoPresence(self.bob)

    def test_join_twice(self):
        self.test_join_empty()
        msg = self.rpcExpectError(self.service, self.alice,
                                  "join", channel="#cats")
        self.assertEqual(msg, "Already joined")

    def test_send_message(self):
        self.test_join_two()

        response = self.rpcCall(self.service, self.alice,
                                "send", channel="#cats", body="Hello")
        self.assertEqual(response, None)

        self.assertMessage(self.alice, "Alice", "Hello")
        self.assertMessage(self.bob, "Alice", "Hello")

    def test_send_message_invalid_channel(self):
        # Alice joins #cats
        self.test_join_empty()

        # Bob joins #operators
        response = self.rpcCall(self.service, self.bob,
                                "join", channel="#operators")
        self.assertMembersEqual(response, ["Bob"])

        msg = self.rpcExpectError(self.service, self.alice,
                                  "send", channel="#operators", body="spam")
        self.assertEqual(msg, "Not joined")

        self.assertNoMessage(self.bob)

    def test_leave_channel(self):
        self.test_join_two()

        # Alice leaves
        response = self.rpcCall(self.service, self.alice,
                                "leave", channel="#cats")
        self.assertEqual(response, None)

        # Bob receives the "left" presence (discard it)
        self.assertPresence(self.bob, "Alice", "left")

        # Bob sends a message
        response = self.rpcCall(self.service, self.bob,
                                "send", channel="#cats", body="Hello")
        self.assertEqual(response, None)

        # Only Bob receives it
        self.assertMessage(self.bob, "Bob", "Hello")
        self.assertNoMessage(self.alice)

    def test_leave_invalid(self):
        msg = self.rpcExpectError(self.service, self.alice,
                                  "leave", channel="#cats")
        self.assertEqual(msg, "Not joined")

    def test_client_disconnected(self):
        self.test_join_two()

        # Alice leaves, this time disconnecting
        self.service.client_disconnected(self.alice)

        # Snorky should not send anything to Alice at this point
        self.assertNoPresence(self.alice)

        # Bob a "left" presence
        self.assertPresence(self.bob, "Alice", "left")

        # Bob sends a message
        response = self.rpcCall(self.service, self.bob,
                                "send", channel="#cats", body="Hello")
        self.assertEqual(response, None)

        # Only Bob receives it
        self.assertMessage(self.bob, "Bob", "Hello")
        self.assertNoMessage(self.alice)


if __name__ == "__main__":
    unittest.main()
