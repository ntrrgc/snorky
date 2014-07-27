import unittest
from mock import Mock
from snorky.services.datasync.subscription import \
        Subscription, SubscriptionItem


class FakeClient(object):
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

    def test_got_client(self):
        subscription = Subscription([self.subscription_item])

        # Client connects
        subscription.got_client(self.client)
        self.assertIs(self.client, subscription.client)
        self.assertEqual(subscription._awaited_client_buffer, [])
        self.assertFalse(self.client.deliver_delta.called)

        # Client disconnects
        subscription.lost_client()
        self.assertIsNone(subscription.client)

    def test_awaited_client_buffer(self):
        subscription = Subscription([self.subscription_item])

        # Send delta
        subscription.deliver_delta(self.delta)

        # Client connects
        subscription.got_client(self.client)

        # Delta should have arrived to client, untouched
        self.client.deliver_delta.assert_called_once_with(self.delta)

        # Awaited client buffer should be empty now
        self.assertEqual(subscription._awaited_client_buffer, [])
