# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from snorky.services.cursors import CursorsService

from mock import Mock
from snorky.tests.utils.rpc import RPCTestMixin
from unittest import TestCase
import unittest


class MockClient(object):
    def __init__(self, identity):
        self.identity = identity
        self.send = Mock()


class TestCursors(RPCTestMixin, TestCase):
    def setUp(self):
        self.alice = MockClient("Alice")
        self.alice_laptop = MockClient("Alice")
        self.bob = MockClient("Bob")
        self.charlie = MockClient("Charlie")
        self.anonymous = MockClient(None)

        self.service = CursorsService("cursors")

    def join(self, client, document, expected_cursors):
        response = self.rpcCall(self.service, client,
                                "join", document=document)
        self.assertEqual(sorted(response["cursors"]),
                         sorted(expected_cursors))

    def assert_cursor(self, client, notification_type, cursor):
        client.send.assert_called_once_with({
            "service": "cursors",
            "message": {
                "type": notification_type,
                "cursor": cursor,
            }
        })
        client.send.reset_mock()

    def assert_no_cursor(self, client):
        self.assertFalse(client.send.called)

    def test_anonymous(self):
        msg = self.rpcExpectError(self.service, self.anonymous,
                                  "join", document="Sheet1")
        self.assertEqual(msg, "Not authenticated")

    def test_join(self):
        self.join(self.alice, "Sheet1", [])
        self.join(self.alice_laptop, "Sheet1", [])
        self.join(self.bob, "Sheet1", [])
        self.join(self.charlie, "Sheet2", [])

    def test_join_twice(self):
        self.test_join()

        msg = self.rpcExpectError(self.service, self.alice,
                                  "join", document="Sheet1")
        self.assertEqual(msg, "Already joined")

    def create_cursor(self, position=12, privateHandle=1):
        response = self.rpcCall(self.service, self.alice,
                                "createCursor", privateHandle=privateHandle,
                                document="Sheet1", position=position,
                                status="focused")
        self.assertIsNotNone(response)
        self.alice_handle = response

        cursor = {
            "publicHandle": self.alice_handle,
            "position": position,
            "status": "focused",
            "owner": "Alice",
            "document": "Sheet1",
        }
        self.assert_cursor(self.bob, "cursorAdded", cursor)
        self.assert_cursor(self.alice_laptop, "cursorAdded", cursor)
        self.assert_no_cursor(self.alice)
        self.assert_no_cursor(self.charlie)

    def test_create_cursor(self):
        self.test_join()
        self.create_cursor()

    def test_create_cursor_twice(self):
        self.test_create_cursor()

        msg = self.rpcExpectError(self.service, self.alice,
                                  "createCursor", privateHandle=1,
                                  document="Sheet1", position=15,
                                  status="focused")
        self.assertEqual(msg, "Reused handle")

    def test_too_many_cursors(self):
        self.test_join()

        for i in range(16):
            self.create_cursor(privateHandle=i)

        msg = self.rpcExpectError(self.service, self.alice,
                                  "createCursor", privateHandle=17,
                                  document="Sheet1", position=10,
                                  status="focused")
        self.assertEqual(msg, "Too many cursors")

        # Alice's laptop can still create more cursors
        response = self.rpcCall(self.service, self.alice_laptop,
                                "createCursor", privateHandle=1,
                                document="Sheet1", position=17,
                                status="focused")
        self.assertIsNotNone(response)
        self.alice_handle2 = response

        cursor = {
            "publicHandle": self.alice_handle2,
            "position": 17,
            "status": "focused",
            "owner": "Alice",
            "document": "Sheet1",
        }
        self.assert_cursor(self.bob, "cursorAdded", cursor)
        self.assert_cursor(self.alice, "cursorAdded", cursor)
        self.assert_no_cursor(self.alice_laptop)
        self.assert_no_cursor(self.charlie)

    def test_move_cursor(self):
        self.test_create_cursor()

        response = self.rpcCall(self.service, self.alice,
                                "updateCursor", privateHandle=1,
                                newData={
                                    "position": 13,
                                    "status": "writing",
                                })
        self.assertEqual(response, None)

        cursor = {
            "publicHandle": self.alice_handle,
            "position": 13,
            "status": "writing",
            "owner": "Alice",
            "document": "Sheet1",
        }
        self.assert_cursor(self.bob, "cursorUpdated", cursor)
        self.assert_cursor(self.alice_laptop, "cursorUpdated", cursor)
        self.assert_no_cursor(self.alice)
        self.assert_no_cursor(self.charlie)

    def test_delete_nonexistent(self):
        msg = self.rpcExpectError(self.service, self.alice,
                                  "removeCursor", privateHandle=15)
        self.assertEqual(msg, "No such cursor")

    def test_update_nonexistent(self):
        msg = self.rpcExpectError(self.service, self.alice,
                                  "updateCursor", privateHandle=15,
                                  newData={
                                      "position": 2,
                                  })
        self.assertEqual(msg, "No such cursor")

    def test_delete_cursor(self):
        self.test_create_cursor()

        response = self.rpcCall(self.service, self.alice,
                                "removeCursor", privateHandle=1)
        self.assertEqual(response, None)

        cursor = {
            "publicHandle": self.alice_handle,
            "document": "Sheet1",
        }
        self.assert_cursor(self.bob, "cursorRemoved", cursor)
        self.assert_cursor(self.alice_laptop, "cursorRemoved", cursor)
        self.assert_no_cursor(self.alice)
        self.assert_no_cursor(self.charlie)

    def test_join_with_cursors(self):
        self.test_create_cursor()

        # Charlie joins now, he should receive Alice's cursor
        self.join(self.charlie, "Sheet1", [{
            "publicHandle": self.alice_handle,
            "position": 12,
            "status": "focused",
            "owner": "Alice",
            "document": "Sheet1",
        }])

    def test_join_two(self):
        self.test_create_cursor()

        # Alice joins another document
        self.join(self.alice, "Sheet2", [])

        self.alice_handle2 = self.rpcCall(self.service, self.alice,
                                          "createCursor", privateHandle=2,
                                          document="Sheet2",
                                          position=1, status="focused")

        cursor = {
            "publicHandle": self.alice_handle2,
            "position": 1,
            "status": "focused",
            "owner": "Alice",
            "document": "Sheet2",
        }
        self.assert_cursor(self.charlie, "cursorAdded", cursor)
        self.assert_no_cursor(self.alice_laptop)
        self.assert_no_cursor(self.bob)
        self.assert_no_cursor(self.alice)

    def test_leave(self):
        self.test_join_two()

        response = self.rpcCall(self.service, self.alice,
                                "leave", document="Sheet1")
        self.assertEqual(response, None)

        # Sheet1's cursor is removed
        cursor = {
            "publicHandle": self.alice_handle,
            "document": "Sheet1",
        }
        self.assert_cursor(self.bob, "cursorRemoved", cursor)
        self.assert_cursor(self.alice_laptop, "cursorRemoved", cursor)
        self.assert_no_cursor(self.alice)
        self.assert_no_cursor(self.charlie)

    def test_leave_not_joined(self):
        msg = self.rpcExpectError(self.service, self.alice,
                                  "leave", document="Sheet3")
        self.assertEqual(msg, "Not joined")

    def test_leave_not_joined2(self):
        # Try it works when the client is already in other documents
        self.test_join_two()
        self.test_leave_not_joined()

    def test_disconnect(self):
        self.test_join_two()

        self.service.client_disconnected(self.alice)

        # Cursor removed notifications shall be sent
        cursor1 = {
            "publicHandle": self.alice_handle,
            "document": "Sheet1",
        }
        cursor2 = {
            "publicHandle": self.alice_handle2,
            "document": "Sheet2",
        }
        self.assert_cursor(self.bob, "cursorRemoved", cursor1)
        self.assert_cursor(self.alice_laptop, "cursorRemoved", cursor1)
        self.assert_cursor(self.charlie, "cursorRemoved", cursor2)
        self.assert_no_cursor(self.alice)

    def test_clean_after_disconnected(self):
        self.test_disconnect()
        self.service.client_disconnected(self.alice_laptop)
        self.service.client_disconnected(self.bob)
        self.service.client_disconnected(self.charlie)
        self.service.client_disconnected(self.anonymous)

        self.assertEqual(len(self.service.cursors_by_client), 0)
        self.assertEqual(len(self.service.cursors_by_document), 0)
        self.assertEqual(len(self.service.clients_by_document), 0)


if __name__ == "__main__":
    unittest.main()
