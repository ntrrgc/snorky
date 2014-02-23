import unittest
from miau.common.delta import Delta, DeltaItemCreation, DeltaItemDeletion
from miau.server.managers.subscription import SubscriptionManager, \
        UnknownSubscription
from miau.server.managers.dealer import DealerManager
from miau.server.dealers import SimpleDealer
from miau.server.subscription import SubscriptionItem
from miau.server.client import Client
from miau.server.facade import Facade
from miau.common.types import StringTypes
from tornado.testing import AsyncTestCase


class TestClient(Client):
    def __init__(self, test_case):
        self.test_case = test_case
        super(TestClient, self).__init__(None)

    def deliver_delta(self, delta):
        self.test_case._deltas_received.append(delta)


class PlayersWithColor(SimpleDealer):
    name = 'players_with_color'
    model_class_name = 'Player'
    
    def get_key_for_model(self, model):
        return model['color']
        

class TestFacade(AsyncTestCase):
    def setUp(self):
        super(TestFacade, self).setUp()
        self._deltas_received = []

        self.dm = DealerManager()
        self.dm.register_dealer(PlayersWithColor())

        self.sm = SubscriptionManager()

        self.facade = Facade(self.dm, self.sm, self.io_loop)

    def test_authorize_subscription(self):
        items = [SubscriptionItem('players_with_color', 'red')]
        token = self.facade.authorize_subscription(items)
        self.assertTrue(isinstance(token, StringTypes))

        return token

    def test_acquire_wrong_subscription(self):
        client = TestClient(self)
        token = "foo_invalid_foo"

        with self.assertRaises(UnknownSubscription):
            self.facade.acquire_subscription(client, token)

    def test_acquire_subscription(self, delta_before=True):
        token = self.test_authorize_subscription()

        client = TestClient(self)

        if delta_before:
            # Send a delta before client connection
            delta = Delta(created=[
                DeltaItemCreation('Player', {
                    'id': 1,
                    'name': 'Alice',
                    'color': 'red'
                })
            ], updated=[], deleted=[])
            self.dm.deliver_delta(delta)

        self.facade.acquire_subscription(client, token)

        # Assert client has the subscription
        subscription = list(client.subscriptions)[0]
        self.assertEqual(subscription.token, token)

        # Assert the timeout has been removed
        self.assertTrue(self.io_loop._cancellations == 1 or \
                self.io_loop._timeouts == [],
                'Subscription timeout has not been removed.')
        self.assertIsNone(subscription._awaited_client_timeout)

        if delta_before:
            # Assert client has received the delta
            self.assertEqual(len(self._deltas_received), 1)

        # Clear _deltas_received
        self._deltas_received[:] = []

        # Send another delta
        delta = Delta(created=[], updated=[], deleted=[
            DeltaItemDeletion('Player', {
                'id': 1,
                'name': 'Alice',
                'color': 'red'
            })
        ])
        self.dm.deliver_delta(delta)

        # Assert it has been received too
        self.assertEqual(len(self._deltas_received), 1)

        self._deltas_received[:] = []

        return client, token

    def test_acquire_subscription_without_delta_before(self):
        return self.test_acquire_subscription(delta_before=False)

    def test_cancel_subscription(self, disconnect=False):
        client, token = self.test_acquire_subscription()

        if disconnect:
            self.facade.client_disconnected(client)
        else:
            self.facade.cancel_subscription(client, token)

        # Assert the client no longer has the subscription
        self.assertEqual(len(client.subscriptions), 0)

        # The dealer should have removed the only subscription item it had, so
        # it should be empty at this time.
        dealer = self.dm.get_dealer("players_with_color")
        self.assertEqual(len(dealer.items_by_model_key), 0)

        # Send a delta
        delta = Delta(created=[
            DeltaItemCreation('Player', {
                'id': 2,
                'name': 'Bob',
                'color': 'red'
            })
        ], updated=[], deleted=[])
        self.dm.deliver_delta(delta)

        # Assert the client has not received it
        self.assertEqual(len(self._deltas_received), 0)

    def test_client_disconnected(self):
        return self.test_cancel_subscription(disconnect=True)

    def test_client_timeout(self, delta_before=True):
        token = self.test_authorize_subscription()

        if delta_before:
            # Send a delta before client connection
            delta = Delta(created=[
                DeltaItemCreation('Player', {
                    'id': 1,
                    'name': 'Alice',
                    'color': 'red'
                })
            ], updated=[], deleted=[])
            self.dm.deliver_delta(delta)

        # Warning: The following code uses some Tornado IOLoop internals, so it
        # may break in the future.

        # Get the timeout callback
        timeout = self.io_loop._timeouts[0]
        callback = timeout.callback

        # Simulate the timeout
        self.io_loop.remove_timeout(timeout)
        callback()

        # Assert the subscription has been deleted
        with self.assertRaises(UnknownSubscription):
            self.sm.get_subscription_with_token(token)

    def test_client_timeout_without_delta_before(self):
        return self.test_client_timeout(delta_before=False)
