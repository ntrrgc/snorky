# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from mock import Mock
from snorky.services.datasync.dealers import FilterDealer, BadQuery
from snorky.services.datasync.delta import \
        InsertionDelta, UpdateDelta, DeletionDelta


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


class MyDealer(FilterDealer):
    name = 'test_dealer'
    model = 'Player'

    def get_key_for_model(self, model):
        return model.prop


class TestSimpleDealer(unittest.TestCase):
    def setUp(self):
        self.model1 = { "color": "blue" }
        self.model2 = { "color": "red" }
        self.item1 = FakeSubscriptionItem(['==', 'color', 'blue'])
        self.item2 = FakeSubscriptionItem(['==', 'color', 'red'])
        self.item3 = FakeSubscriptionItem(['==', 'color', 'blue'])

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
        model3 = { "color": "brown" }
        items = set(dealer.get_subscription_items_for_model(model3))
        self.assertEqual(len(items), 0)

    def test_bad_format(self):
        dealer = MyDealer()

        with self.assertRaises(BadQuery):
            dealer.add_subscription_item(FakeSubscriptionItem({"foo": "bar"}))


if __name__ == "__main__":
    unittest.main()

