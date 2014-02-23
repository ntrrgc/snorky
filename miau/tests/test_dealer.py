import unittest
import miau.server.dealers
import miau.common.delta


class FakeSubscriptionItem(object):
    def __init__(self, callback):
        self.callback = callback

    def deliver_delta(self, delta):
        self.callback(delta)


class DummyModel(object):
    def __init__(self, prop):
        self.prop = prop


class DummyDealer(miau.server.dealers.Dealer):
    name = 'dummy'

    def __init__(self):
        super(DummyDealer, self).__init__()
        self._response = None

    def add_subscription_item(self, item):
        raise NotImplementedError

    def remove_subscription_item(self, item):
        raise NotImplementedError

    def _set_test_subscription_item(self, item):
        self._test_item = item

    def get_subscription_items_for_model(self, model):
        return set([self._test_item])
        set_response = lambda response: setattr(self, '_response', response)

        item1 = FakeSubscriptionItem(set_response)


class TestDealer(unittest.TestCase):
    def setUp(self):
        self._response = None
        self._test_item = FakeSubscriptionItem(
                lambda r: setattr(self, '_response', r))

    def test_name(self):
        dealer = DummyDealer()

        self.assertEqual(dealer.name, 'dummy')

    def test_creation(self):
        dealer = DummyDealer()
        dealer._set_test_subscription_item(self._test_item)

        creation = miau.common.delta.DeltaItemCreation('foo',
                {'id': 1, 'name': 'Alice'})
        dealer.deliver_delta_item(creation)

        r = self._response
        self.assertIsNotNone(r)
        self.assertEqual(len(r.created), 1)
        self.assertEqual(len(r.updated), 0)
        self.assertEqual(len(r.deleted), 0)
        self.assertEqual(r.created[0].data['name'], 'Alice')

    def test_update(self):
        dealer = DummyDealer()
        dealer._set_test_subscription_item(self._test_item)

        update = miau.common.delta.DeltaItemUpdate('foo',
                {'id': 1, 'name': 'Alice'},
                {'id': 1, 'name': 'Bob'})
        dealer.deliver_delta_item(update)

        r = self._response
        self.assertIsNotNone(r)
        self.assertEqual(len(r.created), 0)
        self.assertEqual(len(r.updated), 1)
        self.assertEqual(len(r.deleted), 0)
        self.assertEqual(r.updated[0].old_data['name'], 'Alice')
        self.assertEqual(r.updated[0].new_data['name'], 'Bob')

    def test_deletion(self):
        dealer = DummyDealer()
        dealer._set_test_subscription_item(self._test_item)

        deletion = miau.common.delta.DeltaItemDeletion('foo',
                {'id': 1, 'name': 'Alice'})
        dealer.deliver_delta_item(deletion)

        r = self._response
        self.assertIsNotNone(r)
        self.assertEqual(len(r.created), 0)
        self.assertEqual(len(r.updated), 0)
        self.assertEqual(len(r.deleted), 1)
        self.assertEqual(r.deleted[0].data['name'], 'Alice')


if __name__ == "__main__":
    unittest.main()
