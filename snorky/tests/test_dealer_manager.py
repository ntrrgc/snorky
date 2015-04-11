# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from mock import Mock
from snorky.services.datasync.managers.dealer import \
        DealerManager, UnknownModelClass, UnknownDealer
from snorky.services.datasync.subscription import SubscriptionItem
from snorky.services.datasync.delta import \
        InsertionDelta, UpdateDelta, DeletionDelta


class FakeService(object):
    pass


class FakeSubscription(object):
    def __init__(self, items):
        self.items = items


class FakeDealer(object):
    def __init__(self, name, model):
        self.name = name
        self.model = model

        self.deliver_delta = Mock()
        self.add_subscription_item = Mock()
        self.remove_subscription_item = Mock()

class TestDealerManager(unittest.TestCase):
    def setUp(self):
        self.service = FakeService()

        self.dealer1 = FakeDealer('test_dealer1', 'test_model')
        self.dealer2 = FakeDealer('test_dealer2', 'test_model')

    def test_register_dealer(self):
        dm = DealerManager()

        # Register a dealer
        dm.register_dealer(self.dealer1)
        self.assertIs(dm.get_dealer('test_dealer1'), self.dealer1)
        self.assertEqual(set(dm.get_dealers_for_model_class('test_model')),
                {self.dealer1})

        # Register a second dealer for the same model class
        dm.register_dealer(self.dealer2)
        self.assertIs(dm.get_dealer('test_dealer2'), self.dealer2)
        self.assertEqual(set(dm.get_dealers_for_model_class('test_model')),
                {self.dealer1, self.dealer2})

    def test_get_unregistered_dealer(self):
        dm = DealerManager()

        with self.assertRaises(UnknownDealer):
            dm.get_dealer('foo')

    def test_deliver_delta(self):
        dm = DealerManager()
        dm.register_dealer(self.dealer1)

        # Send a delta of the same model class of the registered dealer
        delta = InsertionDelta('test_model', {'id':1})
        dm.deliver_delta(delta)

        self.dealer1.deliver_delta.assert_called_once_with(delta)

    def test_deliver_delta_without_dealer(self):
        dm = DealerManager()

        # Send a delta of a model class without dealers
        delta = InsertionDelta('test_model', {'id':1})

        with self.assertRaises(UnknownModelClass):
            dm.deliver_delta(delta)

    def test_deliver_delta_other_model_class(self):
        dm = DealerManager()
        dm.register_dealer(self.dealer1)

        # Send a delta of a model class without dealers
        delta = InsertionDelta('unknown_model', {'id':1})

        with self.assertRaises(UnknownModelClass):
            dm.deliver_delta(delta)

    def test_connect_subscription(self):
        dm = DealerManager()
        dm.register_dealer(self.dealer1)

        item = SubscriptionItem("test_dealer1", 5)
        subscription = FakeSubscription([item])

        dm.connect_subscription(subscription)

        self.dealer1.add_subscription_item.assert_called_once_with(item)

        return dm, subscription, item

    def test_disconnect_subscription(self):
        dm, subscription, item = self.test_connect_subscription()

        dm.disconnect_subscription(subscription)

        self.dealer1.add_subscription_item.assert_called_once_with(item)
