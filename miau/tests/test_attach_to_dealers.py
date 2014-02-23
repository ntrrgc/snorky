import unittest
from miau.server.subscription import Subscription, SubscriptionItem
from miau.server.managers.dealer import DealerManager


class FakeDealer(object):
    model_class_name = 'foo_model'
    name = 'test_dealer'

    def __init__(self, callback_add, callback_remove):
        self.callback_add = callback_add
        self.callback_remove = callback_remove

    def add_subscription_item(self, item):
        self.callback_add(item)

    def remove_subscription_item(self, item):
        self.callback_remove(item)


class TestAttachToDealers(unittest.TestCase):
    def setUp(self):
        self._item_add = None
        self._item_remove = None
        self.callback_add = lambda i: setattr(self, '_item_add', i)
        self.callback_remove = lambda i: setattr(self, '_item_remove', i)
        
    def test_attach(self):
        dealer_manager = DealerManager()

        dealer = FakeDealer(self.callback_add, self.callback_remove)
        dealer_manager.register_dealer(dealer)

        item = SubscriptionItem('test_dealer', 'foo_key')
        subscription = Subscription([item])

        self.assertFalse(subscription.attached)
        subscription.attach_to_dealers(dealer_manager)
        self.assertTrue(subscription.attached)
        # Assert add_subscription_item has been called
        self.assertIs(self._item_add, item)

        subscription.dettach_from_dealers(dealer_manager)
        self.assertFalse(subscription.attached)
        # Assert remove_subscription_item has been called
        self.assertIs(self._item_remove, item)
