# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from mock import Mock
from snorky.services.datasync.dealers import SimpleDealer
from snorky.services.datasync.delta import \
        Delta, InsertionDelta, UpdateDelta, DeletionDelta


class FakeService(object):
    pass


class FakeSubscription(object):
    def __init__(self):
        self.deliver_delta = Mock()


class FakeSubscriptionItem(object):
    def __init__(self, query):
        self.subscription = FakeSubscription()
        self.query = query


class DummyModel(object):
    def __init__(self, prop):
        self.prop = prop


class MyDealer(SimpleDealer):
    name = 'test_dealer'
    model = 'dummy (unused)'

    def get_key_for_model(self, model):
        return model.prop


class TestSimpleDealer(unittest.TestCase):
    def setUp(self):
        self.model1 = DummyModel(1)
        self.model2 = DummyModel(2)
        self.item1 = FakeSubscriptionItem(1)
        self.item2 = FakeSubscriptionItem(2)
        self.item3 = FakeSubscriptionItem(1)

    def test_name(self):
        dealer = MyDealer()

        self.assertEqual(dealer.name, 'test_dealer')

    def test_items(self):
        dealer = MyDealer()

        dealer.add_subscription_item(self.item1)
        dealer.add_subscription_item(self.item2)
        dealer.remove_subscription_item(self.item1)
        dealer.add_subscription_item(self.item3)
        dealer.add_subscription_item(self.item1)

        items = set(dealer.get_subscription_items_for_model(self.model1))
        self.assertEqual(items, {self.item1, self.item3})

        items = set(dealer.get_subscription_items_for_model(self.model2))
        self.assertEqual(items, {self.item2})

        # Assert untracked model does not yield subscription items
        items = set(dealer.get_subscription_items_for_model(DummyModel(4)))
        self.assertEqual(len(items), 0)


if __name__ == "__main__":
    unittest.main()
