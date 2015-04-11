# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from mock import Mock
from snorky.services.datasync.subscription import \
        Subscription, SubscriptionItem


class FakeClient(object):
    pass


class FakeService(object):
    def __init__(self):
        self.deliver_delta = Mock()


class FakeDelta(object):
    # Subscription class does not use Delta's methods or properties, just
    # passes the Delta object around.
    pass


class TestSubscription(unittest.TestCase):
    def setUp(self):
        self.subscription_item = SubscriptionItem('test_dealer', 'red')
        self.client = FakeClient()
        self.delta = FakeDelta()
        self.service = FakeService()

    def test_got_client(self):
        subscription = Subscription([self.subscription_item], self.service)

        # Client connects
        subscription.got_client(self.client)
        self.assertIs(self.client, subscription.client)
        self.assertEqual(subscription._awaited_client_buffer, [])
        self.assertFalse(self.service.deliver_delta.called)

        # Client disconnects
        subscription.lost_client()
        self.assertIsNone(subscription.client)

    def test_awaited_client_buffer(self):
        subscription = Subscription([self.subscription_item], self.service)

        # Send delta
        subscription.deliver_delta(self.delta)

        # Client connects
        subscription.got_client(self.client)

        # Delta should have arrived to client, untouched
        self.service.deliver_delta.assert_called_once_with(self.client,
                                                           self.delta)

        # Awaited client buffer should be empty now
        self.assertEqual(subscription._awaited_client_buffer, [])

        # Further messages must arrive directly
        self.service.deliver_delta.reset_mock()
        subscription.deliver_delta(self.delta)
        self.service.deliver_delta.assert_called_once_with(self.client,
                                                           self.delta)
        self.assertEqual(subscription._awaited_client_buffer, [])
