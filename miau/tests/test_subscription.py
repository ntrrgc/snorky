import unittest
from miau.server.subscription import Subscription, SubscriptionItem


class FakeClient(object):
    def __init__(self, callback):
        self.callback = callback

    def deliver_delta(self, delta):
        self.callback(delta)


class FakeDelta(object):
    # Subscription class does not use Delta's methods or properties, just
    # passes the Delta object around.
    pass


class TestSubscription(unittest.TestCase):
    def setUp(self):
        self._received_delta = None
        self.subscription_item = SubscriptionItem('test_dealer', 'red')
        self.client = FakeClient(lambda d: setattr(self, '_received_delta', d))
        self.delta = FakeDelta()
    
    def test_got_client(self):
        subscription = Subscription([self.subscription_item])

        # Client connects
        subscription.got_client(self.client)
        self.assertTrue(subscription.acquired)
        self.assertIs(self.client, subscription.client)
        self.assertEqual(subscription._awaited_client_buffer, [])

        # Client disconnects
        subscription.lost_client()
        self.assertFalse(subscription.acquired)
        self.assertIsNone(subscription.client)

    def test_awaited_client_buffer(self):
        subscription = Subscription([self.subscription_item])

        # Send delta
        subscription.deliver_delta(self.delta)

        # Client connects
        subscription.got_client(self.client)

        # Delta should have arrived to client, untouched
        self.assertIsNotNone(self._received_delta)
        self.assertIs(self._received_delta, self.delta)

        # Awaited client buffer should be empty now
        self.assertEqual(subscription._awaited_client_buffer, [])
