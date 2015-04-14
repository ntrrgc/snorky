# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from mock import Mock
from unittest import TestCase
from snorky.tests.utils.rpc import RPCTestMixin
from snorky.tests.utils.timeout import TestTimeoutFactory
import unittest

from snorky.services.datasync.frontend import DataSyncService
from snorky.services.datasync.backend import DataSyncBackend
from snorky.services.datasync.dealers import SimpleDealer
from snorky.types import is_string


class FakeClient(object):
    def __init__(self):
        self.send = Mock()


class TestDealer(SimpleDealer):
    name = "players_with_color"
    model = "Player"

    def get_key_for_model(self, model):
        return model["color"]


class TestDataSync(RPCTestMixin, TestCase):
    def setUp(self):
        self.time_man = TestTimeoutFactory()
        self.frontend = DataSyncService("frontend")
        self.backend = DataSyncBackend("backend", self.frontend,
                                       timeout_factory=self.time_man)

        self.dm = self.frontend.dm
        self.sm = self.frontend.sm

        self.dealer = TestDealer()
        self.frontend.register_dealer(self.dealer)

        self.client = FakeClient()

    def test_client_disconnected_without_using_the_service(self):
        self.frontend.client_disconnected(self.client)
        # No crash

    def assert_test_delta(self, color):
        self.client.send.assert_called_once_with({
            "service": "frontend",
            "message": {
                "type": "delta",
                "delta": {
                    "type": "insert",
                    "model": "Player",
                    "data": {
                        "name": "Alice",
                        "color": color
                    }
                }
            }
        })
        self.client.send.reset_mock()

    def assert_no_test_delta(self):
        self.assertFalse(self.client.send.called)

    def send_test_delta(self, color):
        response = self.rpcCall(self.backend, None,
                        "publishDeltas", deltas=[{
                            "type": "insert",
                            "model": "Player",
                            "data": {
                                "name": "Alice",
                                "color": color
                            },
                        }])
        self.assertEqual(response, None)

    def test_dealer_is_registered(self):
        self.assertIs(self.dm.dealers_by_name["players_with_color"],
                      self.dealer)
        self.assertIn(self.dealer, self.dm.dealers_by_model["Player"])

    def test_authorize_subscription(self):
        self.token = self.rpcCall(self.backend, None,
                "authorizeSubscription", items=[{
                    "dealer": "players_with_color",
                    "query": "red"
                }])
        self.assertTrue(is_string(self.token))

        # A subscription object is created
        self.assertIn(self.token, self.sm.subscriptions_by_token)
        self.subscription = self.sm.subscriptions_by_token[self.token]

        # The subscription has a timeout
        self.assertIsNotNone(self.subscription._awaited_client_timeout)
        self.assertEqual(self.time_man.timeouts_pending, 1)

    def test_authorize_subscription_bad_dealer_format(self):
        msg = self.rpcExpectError(self.backend, None,
                                  "authorizeSubscription", items=[{
                                      "dealer": {},
                                      "query": "meow",
                                  }])
        self.assertEqual(msg, "dealer should be a dealer name")

    def test_authorize_subscription_bad_format(self):
        msg = self.rpcExpectError(self.backend, None,
                                  "authorizeSubscription", items=[{
                                      "foo": "bar",
                                      "query": "meow",
                                  }])
        self.assertIn("Missing field", msg)

    def test_authorize_subscription_unknown_dealer(self):
        msg = self.rpcExpectError(self.backend, None,
                                  "authorizeSubscription", items=[{
                                      "dealer": "whatever",
                                      "query": "",
                                  }])
        self.assertEqual(msg, "No such dealer")

    def test_acquire_subscription(self):
        self.test_authorize_subscription()

        # TODO Check if queued messages get delivered before or after this call
        response = self.rpcCall(self.frontend, self.client,
                                "acquireSubscription", token=self.token)
        self.assertEqual(response, None)

        # Subscription is linked now
        self.assertIs(self.subscription.client, self.client)

        # Timeout has been cleared
        self.assertIsNone(self.subscription._awaited_client_timeout)
        self.assertEqual(self.time_man.timeouts_pending, 0)

    def test_acquire_wrong_subscription(self):
        msg = self.rpcExpectError(self.frontend, self.client,
                                  "acquireSubscription", token="foo")
        self.assertEqual(msg, "No such subscription")

    def test_acquire_subscription_invalid_token(self):
        msg = self.rpcExpectError(self.frontend, self.client,
                                  "acquireSubscription", token=1)
        self.assertEqual(msg, "token must be string")

    def test_delta(self):
        self.test_acquire_subscription()

        self.send_test_delta("red")

        # Test client must have received the delta
        self.assert_test_delta("red")

    def test_delta_other(self):
        self.test_acquire_subscription()

        self.send_test_delta("blue")

        # Test client must have not received the delta
        self.assert_no_test_delta()

    def test_disconnect(self):
        self.test_acquire_subscription()

        self.frontend.client_disconnected(self.client)

        self.send_test_delta("red")

        # Test client must have not received the delta
        self.assert_no_test_delta()

    def test_delta_before(self):
        self.test_authorize_subscription()

        self.send_test_delta("red")

        # Test client can't have received anything since it has not connected
        # yet.
        self.assert_no_test_delta()

        # Client connects now
        response = self.rpcCall(self.frontend, self.client,
                        "acquireSubscription", token=self.token)
        self.assertEqual(response, None)

        self.assert_test_delta("red")

    def test_timeout(self):
        self.test_authorize_subscription()

        self.send_test_delta("red")

        self.assertIn(self.token, self.frontend.sm.subscriptions_by_token)

        # Let the time pass...
        self.time_man.process_all()

        self.assertNotIn(self.token, self.frontend.sm.subscriptions_by_token)

    def test_cancel_subscription(self):
        self.test_acquire_subscription()

        response = self.rpcCall(self.frontend, self.client,
                                "cancelSubscription", token=self.token)
        self.assertEqual(response, None)

        self.assertNotIn(self.token, self.frontend.sm.subscriptions_by_token)
        self.assertFalse(self.frontend.sm.subscriptions_by_client.in_set(
            self.client, self.subscription))

        self.send_test_delta("red")
        self.assert_no_test_delta()

    def test_cancel_subscription_wrong_token(self):
        msg = self.rpcExpectError(self.frontend, self.client,
                                  "cancelSubscription", token=5)
        self.assertEqual(msg, "token must be string")

    def test_cancel_subscription_invalid_token(self):
        msg = self.rpcExpectError(self.frontend, self.client,
                                  "cancelSubscription", token="foo")
        self.assertEqual(msg, "No such subscription")

    def test_cancel_subscription_other_client(self):
        self.test_acquire_subscription()

        # Clients shall no cancel others' subscriptions
        another_client = FakeClient()
        msg = self.rpcExpectError(self.frontend, another_client,
                                  "cancelSubscription", token=self.token)
        self.assertEqual(msg, "No such subscription")

    def test_register_dealer_class(self):
        self.frontend = DataSyncService("frontend")
        self.frontend.register_dealer(TestDealer)

        # Assign other variables to the new frontend
        self.backend = DataSyncBackend("backend", self.frontend,
                                       timeout_factory=self.time_man)

        self.dm = self.frontend.dm
        self.sm = self.frontend.sm

        # Run the entire test with the new service instances
        self.test_acquire_subscription()

    def test_register_dealer_constructor(self):
        self.frontend = DataSyncService("frontend", [TestDealer])

        # Assign other variables to the new frontend
        self.backend = DataSyncBackend("backend", self.frontend,
                                       timeout_factory=self.time_man)

        self.dm = self.frontend.dm
        self.sm = self.frontend.sm

        # Run the entire test with the new service instances
        self.test_acquire_subscription()

    def test_unregister_dealer(self):
        self.frontend.unregister_dealer(self.dealer)

        msg = self.rpcExpectError(self.backend, None,
                                  "authorizeSubscription", items=[{
                                      "dealer": "players_with_color",
                                      "query": "red"
                                  }])
        self.assertEqual(msg, "No such dealer")

    def test_deletion_delta(self):
        self.test_acquire_subscription()

        response = self.rpcCall(self.backend, None,
                        "publishDeltas", deltas=[{
                            "type": "delete",
                            "model": "Player",
                            "data": {
                                "name": "Alice",
                                "color": "red"
                            },
                        }])
        self.assertEqual(response, None)

        self.client.send.assert_called_once_with({
            "service": "frontend",
            "message": {
                "type": "delta",
                "delta": {
                    "type": "delete",
                    "model": "Player",
                    "data": {
                        "name": "Alice",
                        "color": "red"
                    }
                }
            }
        })

    def test_update_delta(self):
        self.test_acquire_subscription()

        response = self.rpcCall(self.backend, None,
                        "publishDeltas", deltas=[{
                            "type": "update",
                            "model": "Player",
                            "oldData": {
                                "name": "Alice",
                                "color": "red",
                                "points": 0,
                            },
                            "newData": {
                                "name": "Alice",
                                "color": "red",
                                "points": 1,
                            },
                        }])
        self.assertEqual(response, None)

        self.client.send.assert_called_once_with({
            "service": "frontend",
            "message": {
                "type": "delta",
                "delta": {
                    "type": "update",
                    "model": "Player",
                    "oldData": {
                        "name": "Alice",
                        "color": "red",
                        "points": 0,
                    },
                    "newData": {
                        "name": "Alice",
                        "color": "red",
                        "points": 1,
                    },
                }
            }
        })
