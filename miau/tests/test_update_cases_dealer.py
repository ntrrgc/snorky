import simplejson as json
import unittest
import miau.server.dealers
from miau.common.delta import Delta, DeltaItem, DeltaItemCreation, \
        DeltaItemUpdate, DeltaItemDeletion


class FakeSubscriptionItem(object):
    def __init__(self, dealer_name, model_key, callback, subscription=None):
        self.dealer_name = dealer_name
        self.model_key = model_key
        self.callback = callback
        self.subscription = subscription
        
    def deliver_delta(self, delta):
        self.callback(delta)


class PlayersWithColorDealer(miau.server.dealers.SimpleDealer):
    name = 'players_with_color'

    def get_key_for_model(self, model):
        return model['color']


class TestUpdateCasesDealer(unittest.TestCase):
    def setUp(self):
        self._response = None
        self.subscription_item = FakeSubscriptionItem(
                'players_with_color', 'red',
                lambda r: setattr(self, '_response', r))

    def dict_response(self):
        return json.loads(self._response.jsonify())

    def test_unrelated_creation(self):
        dealer = PlayersWithColorDealer()
        dealer.add_subscription_item(self.subscription_item)

        # Alice record is created with color blue
        origin_delta = DeltaItemCreation('player', 
                {'id': 1, 'name': 'Alice', 'color': 'blue'})

        dealer.deliver_delta_item(origin_delta)

        self.assertIsNone(self._response)

    def test_update_creation(self):
        dealer = PlayersWithColorDealer()
        dealer.add_subscription_item(self.subscription_item)

        # Alice changes her color
        origin_delta = DeltaItemUpdate('player', 
                old_data={'id': 1, 'name': 'Alice', 'color': 'blue'},
                new_data={'id': 1, 'name': 'Alice', 'color': 'red'})

        dealer.deliver_delta_item(origin_delta)

        # Subscription item should receive a creation
        self.assertIsNotNone(self._response)
        self.assertEqual(self.dict_response(), {
            'created': [{
                'model_class_name': 'player',
                'data': {
                    'id': 1,
                    'name': 'Alice',
                    'color': 'red',
                }
            }],
            'updated': [],
            'deleted': []
        })

    def test_update_update(self):
        dealer = PlayersWithColorDealer()
        dealer.add_subscription_item(self.subscription_item)

        # Alice changes her player name
        origin_delta = DeltaItemUpdate('player', 
                old_data={'id': 1, 'name': 'Alice', 'color': 'red'},
                new_data={'id': 1, 'name': 'SuperAlice', 'color': 'red'})

        dealer.deliver_delta_item(origin_delta)

        # Subscription item should receive an update
        self.assertIsNotNone(self._response)
        self.assertEqual(self.dict_response(), {
            'created': [],
            'updated': [{
                'model_class_name': 'player',
                'old_data': {
                    'id': 1,
                    'name': 'Alice',
                    'color': 'red',
                },
                'new_data': {
                    'id': 1,
                    'name': 'SuperAlice',
                    'color': 'red',
                }
            }],
            'deleted': []
        })

    def test_update_deletion(self):
        dealer = PlayersWithColorDealer()
        dealer.add_subscription_item(self.subscription_item)

        # Alice changes her color
        origin_delta = DeltaItemUpdate('player', 
                old_data={'id': 1, 'name': 'SuperAlice', 'color': 'red'},
                new_data={'id': 1, 'name': 'SuperAlice', 'color': 'blue'})

        dealer.deliver_delta_item(origin_delta)

        # Subscription item should receive a deletion
        self.assertIsNotNone(self._response)
        self.assertEqual(self.dict_response(), {
            'created': [],
            'updated': [],
            'deleted': [{
                'model_class_name': 'player',
                'data': {
                    'id': 1,
                    'name': 'SuperAlice',
                    'color': 'red',
                },
            }],
        })

    def test_unrelated_deletion(self):
        dealer = PlayersWithColorDealer()
        dealer.add_subscription_item(self.subscription_item)

        # Alice record is deleted
        origin_delta = DeltaItemDeletion('player', 
                {'id': 1, 'name': 'SuperAlice', 'color': 'blue'})

        dealer.deliver_delta_item(origin_delta)

        # Our subscription item has model_key = red, so no response should
        # arrive.
        self.assertIsNone(self._response)


if __name__ == "__main__":
    unittest.main()
