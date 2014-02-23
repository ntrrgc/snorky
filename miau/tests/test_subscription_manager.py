import unittest
from miau.server.managers.subscription import SubscriptionManager, \
        UnknownSubscription
from miau.server.subscription import Subscription, SubscriptionItem


class TestSubscriptionManager(unittest.TestCase):
    def setUp(self):
        pass

    def test_authorize_subscription(self):
        sm = SubscriptionManager()

        item = SubscriptionItem('foo_dealer', 'foo_key')
        subscription = Subscription([item])

        # Authorize subscription
        token = sm.register_subscription(subscription)
        self.assertIsNotNone(token)

        # Get the subscription using its token
        self.assertIs(sm.get_subscription_with_token(token), subscription)
        # Assert the subscription now has the right token
        self.assertEqual(subscription.token, token)

        # Remove subscription
        sm.unregister_subscription(subscription)

        # Assert subscription has no token now
        self.assertIsNone(subscription.token)
        # Assert subscription can't be recovered now
        with self.assertRaises(UnknownSubscription):
            sm.get_subscription_with_token(token)
