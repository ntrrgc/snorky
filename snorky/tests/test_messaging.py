import unittest
from miau.common.types import is_string
from snorky.server.services.messaging import MessagingService


class MockClient(object):
    def __init__(self, test, msg_prop):
        self.test = test
        self.msg_prop = msg_prop

    def send(self, msg):
        setattr(self.test, self.msg_prop, msg)


class TestMessagingService(MessagingService):
    def is_name_allowed(self, client, name):
        return is_string(name) and "duck" not in name.lower()


class TestMessaging(unittest.TestCase):
    def setUp(self):
        self.service = TestMessagingService("messaging")
        self.msg_alice = None
        self.msg_bob = None
        self.msg_carol = None
        self.alice = MockClient(self, "msg_alice")
        self.bob = MockClient(self, "msg_bob")
        self.carol = MockClient(self, "msg_carol")

    def test_register(self):
        self.service.process_message_from(self.alice, {
            "command": "register_participant",
            "call_id": 1,
            "params": {
                "name": "Alice"
            }
        })
        self.assertEqual(self.msg_alice, {
            "service": "messaging",
            "message": {
                "type": "response",
                "call_id": 1,
                "data": None
            }
        })

    def test_register_twice(self):
        # Register Alice first
        self.test_register()

        # Now register Bob
        self.service.process_message_from(self.bob, {
            "command": "register_participant",
            "call_id": 1,
            "params": {
                "name": "Bob"
            }
        })
        self.assertEqual(self.msg_bob, {
            "service": "messaging",
            "message": {
                "type": "response",
                "call_id": 1,
                "data": None
            }
        })

    def test_register_same_name(self):
        # Register Alice first
        self.test_register()

        # Try to register Alice again
        self.service.process_message_from(self.alice, {
            "command": "register_participant",
            "call_id": 2,
            "params": {
                "name": "Alice"
            }
        })
        self.assertEqual(self.msg_alice, {
            "service": "messaging",
            "message": {
                "type": "error",
                "call_id": 2,
                "message": "Name already registered"
            }
        })

    def test_banned_name(self):
        self.service.process_message_from(self.alice, {
            "command": "register_participant",
            "call_id": 1,
            "params": {
                "name": "DrDuck"
            }
        })
        self.assertEqual(self.msg_alice, {
            "service": "messaging",
            "message": {
                "type": "error",
                "call_id": 1,
                "message": "Name not allowed"
            }
        })

    def test_send(self):
        # Register both Alice and Bob
        self.test_register_twice()

        # Alice sends a message to Bob
        self.service.process_message_from(self.alice, {
            "command": "send",
            "call_id": 1,
            "params": {
                "sender": "Alice",
                "dest": "Bob",
                "body": "Hi, Bob."
            }
        })
        self.assertEqual(self.msg_alice, {
            "service": "messaging",
            "message": {
                "type": "response",
                "call_id": 1,
                "data": None
            }
        })
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
        self.service.process_message_from(self.carol, {
            "command": "register_participant",
            "call_id": 1,
            "params": {
                "name": "Carol"
            }
        })
        self.assertEqual(self.msg_carol, {
            "service": "messaging",
            "message": {
                "type": "response",
                "call_id": 1,
                "data": None
            }
        })

    def test_send_forgery(self):
        # Register Alice, Bob and Carol
        self.test_register_twice()

        # Alice tries to send a message to Bob, pretending to be Carol
        self.msg_bob = None
        self.service.process_message_from(self.alice, {
            "command": "send",
            "call_id": 1,
            "params": {
                "sender": "Carol",
                "dest": "Bob",
                "body": "Hi, Bob."
            }
        })
        self.assertEqual(self.msg_alice, {
            "service": "messaging",
            "message": {
                "type": "error",
                "call_id": 1,
                "message": "Invalid sender"
            }
        })
        # Bob has not received anything
        self.assertIsNone(self.msg_bob)

    def test_send_non_existing_sender(self):
        # Register Alice, Bob and Carol
        self.test_register_twice()

        # Alice tries to send a message to Bob with invalid sender
        self.msg_bob = None
        self.service.process_message_from(self.alice, {
            "command": "send",
            "call_id": 1,
            "params": {
                "sender": "Charlie",
                "dest": "Bob",
                "body": "Hi, Bob."
            }
        })
        self.assertEqual(self.msg_alice, {
            "service": "messaging",
            "message": {
                "type": "error",
                "call_id": 1,
                "message": "Invalid sender"
            }
        })
        # Bob has not received anything
        self.assertIsNone(self.msg_bob)

    def test_send_non_existing_recipient(self):
        self.test_register_twice()

        self.service.process_message_from(self.alice, {
            "command": "send",
            "call_id": 1,
            "params": {
                "sender": "Alice",
                "dest": "Charlie",
                "body": "Hi, Charlie."
            }
        })
        self.assertEqual(self.msg_alice, {
            "service": "messaging",
            "message": {
                "type": "error",
                "call_id": 1,
                "message": "Unknown destination"
            }
        })

    def test_list_participants(self):
        self.test_register_three()

        self.service.process_message_from(self.alice, {
            "command": "list_participants",
            "call_id": 1,
            "params": {}
        })
        self.assertEqual(self.msg_alice, {
            "service": "messaging",
            "message": {
                "type": "response",
                "call_id": 1,
                "data": ["Alice", "Bob", "Carol"]
            }
        })

if __name__ == "__main__":
    unittest.main()
