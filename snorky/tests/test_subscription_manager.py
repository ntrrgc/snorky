# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from mock import Mock
from snorky.services.datasync.subscription import \
        Subscription, SubscriptionItem
from snorky.services.datasync.managers.subscription import \
        SubscriptionManager


class FakeSubscription(object):
    def __init__(self):
        self.token = None

        self.got_client = Mock(side_effect=self._got_client)
        self.lost_client = Mock()

    def _got_client(self, client):
        self.client = client


class FakeClient(object):
    pass


class TestSubscriptionManager(unittest.TestCase):
    def setUp(self):
        self.sm = SubscriptionManager()

        self.subscription = FakeSubscription()

    def test_authorize_subscription(self):
        # Authorize subscription
        token = self.sm.register_subscription(self.subscription)
        # A token is generated
        self.assertIsNotNone(token)

        # Get the subscription using its token
        self.assertIs(self.sm.get_subscription_with_token(token),
                      self.subscription)
        # Assert the subscription now has the right token
        self.assertEqual(self.subscription.token, token)

        return token

    def test_remove_subscription(self):
        token = self.test_authorize_subscription()

        # Remove subscription
        self.sm.unregister_subscription(self.subscription)

        # Assert subscription has no token now
        self.assertIsNone(self.subscription.token)
        # Assert subscription can't be recovered now
        self.assertIsNone(self.sm.get_subscription_with_token(token))

    def test_link_to_client(self):
        token = self.test_authorize_subscription()

        client = FakeClient()
        subscription = self.sm.get_subscription_with_token(token)
        self.sm.link_subscription_to_client(subscription, client)

        self.subscription.got_client.assert_called_with(client)
        self.assertTrue(self.sm.subscriptions_by_client.in_set(
            client, subscription))

        return subscription, client

    def test_unlink_from_client(self):
        subscription, client = self.test_link_to_client()

        self.sm.unlink_subscription_from_client(subscription)

        self.subscription.lost_client.assert_called_with()
        self.assertFalse(self.sm.subscriptions_by_client.in_set(
            client, subscription))
