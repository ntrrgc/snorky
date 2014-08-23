import unittest
from snorky.services.datasync.dealers import BroadcastDealer

class FooBroadcastDealer(BroadcastDealer):
    model = "foobar (unused)"


class TestBroadcastDealer(unittest.TestCase):
    def setUp(self):
        self.item1, self.item2, self.item3 = 1, 2, 3

    def test_name(self):
        dealer = FooBroadcastDealer()

        self.assertEqual(dealer.name, 'broadcast')

    def test_items(self):
        dealer = FooBroadcastDealer()

        # Assert no subscription items are tracked yet
        items = set(dealer.get_subscription_items_for_model('foo'))
        self.assertEqual(len(items), 0)

        dealer.add_subscription_item(self.item1)
        dealer.add_subscription_item(self.item2)
        dealer.remove_subscription_item(self.item1)
        dealer.add_subscription_item(self.item3)

        items = set(dealer.get_subscription_items_for_model('foo'))
        self.assertEqual(items, {2, 3})


if __name__ == "__main__":
    unittest.main()
