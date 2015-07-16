# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from mock import Mock
from snorky.services.datasync.dealers import Dealer, BroadcastDealer
from snorky.services.datasync.delta import \
        Delta, InsertionDelta, UpdateDelta, DeletionDelta


class FakeService(object):
    pass


class FakeSubscription(object):
    def __init__(self):
        self.deliver_delta = Mock()


class FakeSubscriptionItem(object):
    def __init__(self):
        self.subscription = FakeSubscription()

class DealerDefaultName(BroadcastDealer):
    pass

class DummyDealer(Dealer):
    name = 'dummy'
    model = 'foobar (unused)'

    def __init__(self, test_item):
        super(DummyDealer, self).__init__()
        self.test_item = test_item

    def add_subscription_item(self, item):
        raise NotImplementedError

    def remove_subscription_item(self, item):
        raise NotImplementedError

    def get_subscription_items_for_model(self, model):
        return set([self.test_item])


class TestDealer(unittest.TestCase):
    def setUp(self):
        self.service = FakeService()
        self.test_item = FakeSubscriptionItem()
        # Shorthand
        self.deliver_delta = self.test_item.subscription.deliver_delta

        self.dealer = DummyDealer(self.test_item)

    def test_name(self):
        self.assertEqual(self.dealer.name, 'dummy')

    def test_default_name(self):
        self.assertEqual(DealerDefaultName().name, "DealerDefaultName")

    def test_insertion(self):
        insertion = InsertionDelta('foo', {'id': 1, 'name': 'Alice'})
        self.dealer.deliver_delta(insertion)

        self.deliver_delta.assert_called_once_with(insertion)

    def test_update(self):
        update = UpdateDelta('foo',
                {'id': 1, 'name': 'Alice'},
                {'id': 1, 'name': 'Bob'})
        self.dealer.deliver_delta(update)

        self.deliver_delta.assert_called_once_with(update)

    def test_deletion(self):
        deletion = DeletionDelta('foo', {'id': 1, 'name': 'Alice'})
        self.dealer.deliver_delta(deletion)

        self.deliver_delta.assert_called_once_with(deletion)


class AutomaticNameDealer(Dealer):
    model = "foobar (unused)"

    def add_subscription_item(self, item):
        raise NotImplementedError

    def remove_subscription_item(self, item):
        raise NotImplementedError

    def get_subscription_items_for_model(self, model):
        raise NotImplementedError


class TestAutomaticNameDealer(unittest.TestCase):
    def test_name(self):
        self.assertEqual(AutomaticNameDealer().name, "AutomaticNameDealer")


if __name__ == "__main__":
    unittest.main()
