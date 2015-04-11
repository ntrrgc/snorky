# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
        self.alice_laptop = MockClient("Alice")
        self.bob = MockClient("Bob")
        self.anonymous = MockClient(None)

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

    def assertPresences(self, client, presences):
        # (identity, status, channel)
        presences_received = set()

        for call_object in client.send.call_args_list:
            args = call_object[0]
            presence = args[0]["message"]
            self.assertEqual(presence["type"], "presence")
            presences_received.add((
                presence["from"],
                presence["status"],
                presence["channel"],
            ))

        self.assertEqual(presences_received, set(presences))
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

    def join(self, client, channel, members):
        response = self.rpcCall(self.service, client,
                                "join", channel=channel)
        self.assertMembersEqual(response, members)
        self.assertNoPresence(client)

    def test_join_empty(self):
        self.join(self.alice, "#cats", ["Alice"])

    def test_join_two(self):
        self.test_join_empty()

        self.join(self.bob, "#cats", ["Alice", "Bob"])

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
        self.join(self.bob, "#operators", ["Bob"])

        # Alice tries to send message to #operators
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

    def test_two_user_three_clients(self):
        # Alice and Bob join the chat
        self.test_join_two()

        # Everybody starts clean
        self.assertNoPresence(self.alice)
        self.assertNoPresence(self.alice_laptop)
        self.assertNoPresence(self.bob)

        # Alice now logs in from her laptop and joins again
        self.join(self.alice_laptop, "#cats", ["Alice", "Bob"])

        # Nobody recives a presence
        self.assertNoPresence(self.alice)
        self.assertNoPresence(self.alice_laptop)
        self.assertNoPresence(self.bob)

        # Bob sends a message
        response = self.rpcCall(self.service, self.bob,
                                "send", channel="#cats", body="Hi")
        self.assertEqual(response, None)

        # Everybody gets the message
        self.assertMessage(self.alice, "Bob", "Hi")
        self.assertMessage(self.alice_laptop, "Bob", "Hi")
        self.assertMessage(self.bob, "Bob", "Hi")

        # Alice sends a message with her first computer
        response = self.rpcCall(self.service, self.alice,
                                "send", channel="#cats", body="What's up?")
        self.assertEqual(response, None)

        # Everybody gets the message
        self.assertMessage(self.alice, "Alice", "What's up?")
        self.assertMessage(self.alice_laptop, "Alice", "What's up?")
        self.assertMessage(self.bob, "Alice", "What's up?")

        # Alice sends a message with her last computer
        response = self.rpcCall(self.service, self.alice_laptop,
                                "send", channel="#cats", body="testing")
        self.assertEqual(response, None)

        # Everybody gets the message
        self.assertMessage(self.alice, "Alice", "testing")
        self.assertMessage(self.alice_laptop, "Alice", "testing")
        self.assertMessage(self.bob, "Alice", "testing")

    def test_leaving_from_two_computers(self):
        self.test_two_user_three_clients()

        # Alice turns off her desktop computer
        self.service.client_disconnected(self.alice)
        self.assertNoPresence(self.alice)

        # Nobody should receive a presence as Alice is still online in her
        # laptop
        self.assertNoPresence(self.alice_laptop)
        self.assertNoPresence(self.bob)

        # Bob sends a message
        response = self.rpcCall(self.service, self.bob,
                                "send", channel="#cats", body="Hi")
        self.assertEqual(response, None)

        # The message arrives to the connected destinations
        self.assertMessage(self.alice_laptop, "Bob", "Hi")
        self.assertMessage(self.bob, "Bob", "Hi")
        self.assertNoMessage(self.alice)

        # Alice disconnects her laptop too
        self.service.client_disconnected(self.alice_laptop)
        self.assertNoPresence(self.alice)
        self.assertNoPresence(self.alice_laptop)
        self.assertPresence(self.bob, "Alice", "left")

    def test_presences_across_several_channels(self):
        self.join(self.alice, "#cats", ["Alice"])
        self.join(self.alice_laptop, "#cats", ["Alice"])
        self.join(self.bob, "#cats", ["Alice", "Bob"])

        self.assertPresence(self.alice, "Bob", "joined")
        self.assertPresence(self.alice_laptop, "Bob", "joined")

        self.join(self.alice, "#dogs", ["Alice"])
        self.join(self.bob, "#dogs", ["Alice", "Bob"])

        self.assertPresence(self.alice, "Bob", "joined", "#dogs")

        self.service.client_disconnected(self.alice)
        self.assertPresences(self.bob, [
            ("Alice", "left", "#dogs")
        ])

        self.service.client_disconnected(self.alice_laptop)
        self.assertPresences(self.bob, [
            ("Alice", "left", "#cats")
        ])

    def test_join_anonymous(self):
        msg = self.rpcExpectError(self.service, self.anonymous,
                                  "join", channel="#cats")
        self.assertEqual(msg, "Not authenticated")

    def assertReadNotification(self, client, channel="#cats"):
        client.send.assert_called_once_with({
            "service": "chat",
            "message": {
                "type": "read",
                "channel": channel,
                "timestamp": "fake",
            }
        })
        client.send.reset_mock()

    def assertNoReadNotification(self, client):
        self.assertFalse(client.send.called)

    def test_read(self):
        self.join(self.alice, "#cats", ["Alice"])
        self.join(self.alice_laptop, "#cats", ["Alice"])
        self.join(self.bob, "#cats", ["Alice", "Bob"])

        self.assertPresence(self.alice, "Bob", "joined")
        self.assertPresence(self.alice_laptop, "Bob", "joined")

        response = self.rpcCall(self.service, self.bob,
                                "send", channel="#cats", body="Hi")
        self.assertEqual(response, None)

        self.assertMessage(self.bob, "Bob", "Hi")
        self.assertMessage(self.alice, "Bob", "Hi")
        self.assertMessage(self.alice_laptop, "Bob", "Hi")

        # Alice reads the message in her desktop
        response = self.rpcCall(self.service, self.alice,
                                "read", channel="#cats")
        self.assertEqual(response, None)

        # Her laptop should have received a read notification
        self.assertReadNotification(self.alice_laptop)
        self.assertNoReadNotification(self.alice)
        self.assertNoReadNotification(self.bob)

if __name__ == "__main__":
    unittest.main()
