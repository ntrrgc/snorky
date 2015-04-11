# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
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
        self.query = query
        self.subscription = FakeSubscription()


class PlayersWithColorDealer(SimpleDealer):
    name = 'players_with_color'
    model = 'Player'

    def get_key_for_model(self, model):
        return model['color']


class TestUpdateCasesDealer(unittest.TestCase):
    def setUp(self):
        self.service = FakeService()
        self.subscription_item = FakeSubscriptionItem('red')
        self.deliver_delta = self.subscription_item.subscription.deliver_delta

    def test_unrelated_creation(self):
        dealer = PlayersWithColorDealer()
        dealer.add_subscription_item(self.subscription_item)

        # Alice record is created with color blue
        original_delta = InsertionDelta('player',
                {'id': 1, 'name': 'Alice', 'color': 'blue'})

        dealer.deliver_delta(original_delta)

        # No delta is received
        self.assertFalse(self.deliver_delta.called)

    def test_update_creation(self):
        dealer = PlayersWithColorDealer()
        dealer.add_subscription_item(self.subscription_item)

        # Alice changes her color
        original_delta = UpdateDelta('player',
                old_data={'id': 1, 'name': 'Alice', 'color': 'blue'},
                new_data={'id': 1, 'name': 'Alice', 'color': 'red'})

        dealer.deliver_delta(original_delta)

        # Subscription item should receive a creation
        self.deliver_delta.assert_called_once_with(
            InsertionDelta("player", {
                'id': 1,
                'name': 'Alice',
                'color': 'red'
            }))

    def test_update_update(self):
        dealer = PlayersWithColorDealer()
        dealer.add_subscription_item(self.subscription_item)

        # Alice changes her player name
        original_delta = UpdateDelta('player',
                old_data={'id': 1, 'name': 'Alice', 'color': 'red'},
                new_data={'id': 1, 'name': 'SuperAlice', 'color': 'red'})

        dealer.deliver_delta(original_delta)

        # Subscription item should receive an update
        self.deliver_delta.assert_called_once_with(original_delta)

    def test_update_deletion(self):
        dealer = PlayersWithColorDealer()
        dealer.add_subscription_item(self.subscription_item)

        # Alice changes her color
        original_delta = UpdateDelta('player',
                old_data={'id': 1, 'name': 'SuperAlice', 'color': 'red'},
                new_data={'id': 1, 'name': 'SuperAlice', 'color': 'blue'})

        dealer.deliver_delta(original_delta)

        # Subscription item should receive a deletion
        self.deliver_delta.assert_called_once_with(
            DeletionDelta('player', {
                'id': 1,
                'name': 'SuperAlice',
                'color': 'red'
            }))

    def test_unrelated_deletion(self):
        dealer = PlayersWithColorDealer()
        dealer.add_subscription_item(self.subscription_item)

        # Alice record is deleted
        original_delta = DeletionDelta('player',
                {'id': 1, 'name': 'SuperAlice', 'color': 'blue'})

        dealer.deliver_delta(original_delta)

        # Our subscription item has query = red, so no response should
        # arrive.
        self.assertFalse(self.deliver_delta.called)


if __name__ == "__main__":
    unittest.main()
