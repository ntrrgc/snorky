import unittest
import miau.server.dealers


class FakeSubscriptionItem(object):
    def __init__(self, model_key):
        self.model_key = model_key


class DummyModel(object):
    def __init__(self, prop):
        self.prop = prop


class MyDealer(miau.server.dealers.SimpleDealer):
    name = 'test_dealer'

    def get_key_for_model(self, model):
        return model.prop


class TestSimpleDealer(unittest.TestCase):
    def setUp(self):
        self.model1, self.model2 = DummyModel(1), DummyModel(2)
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
