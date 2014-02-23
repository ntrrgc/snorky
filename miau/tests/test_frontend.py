import unittest
import simplejson as json
from miau.server.frontend import FrontendHandler
from miau.server.managers.dealer import DealerManager
from miau.server.managers.subscription import SubscriptionManager, \
        UnknownSubscription
from miau.server.dealers import SimpleDealer
from miau.server.subscription import SubscriptionItem
from miau.server.facade import Facade
from miau.common.delta import Delta, DeltaItemCreation
from tornado.testing import ExpectLog, AsyncTestCase


class PlayersWithColor(SimpleDealer):
    name = 'players_with_color'
    model_class_name = 'Player'
    
    def get_key_for_model(self, model):
        return model['color']


class TestableFrontendHandler(FrontendHandler):
    def __init__(self, facade):
        super(TestableFrontendHandler, self).__init__(facade)

        # Used for testing sent messages
        self._sent_message = None
    
    def write_message(self, message):
        self._sent_message = message


class TestFrontend(AsyncTestCase):
    def setUp(self):
        super(TestFrontend, self).setUp()

        self.dm = DealerManager()
        self.sm = SubscriptionManager()

        # Add a Dealer
        dealer = PlayersWithColor()
        self.dm.register_dealer(dealer)

        self.facade = Facade(self.dm, self.sm, self.io_loop)

    def test_acquire_subscription(self):
        # Authorize a subscription first
        items = [SubscriptionItem('players_with_color', 'red')]
        token = self.facade.authorize_subscription(items)

        # Create test client handler
        client_handler = TestableFrontendHandler(self.facade)

        # The client connects
        client_handler.open()

        # The client sends a message to acquire subscription
        client_handler.on_message(json.dumps({
            "call_id": 1,
            "function": "acquire_subscription",
            "token": token
        }))

        # They should have received a success message
        self.assertEqual(json.loads(client_handler._sent_message), {
            "type": "function_response",
            "call_id": 1,
            "status_code": 204
        })

        # The client should have a subscription now
        self.assertEqual(len(client_handler.client.subscriptions), 1)

        return client_handler, token

    def test_cancel_subscription(self):
        # Acquire a subscription
        client_handler, token = self.test_acquire_subscription()

        # The client sends a message to cancel it
        client_handler.on_message(json.dumps({
            "call_id": 2,
            "function": "cancel_subscription",
            "token": token
        }))

        # They should have received a success message
        self.assertEqual(json.loads(client_handler._sent_message), {
            "type": "function_response",
            "call_id": 2,
            "status_code": 204
        })

        # The client should have zero subscriptions now
        self.assertEqual(len(client_handler.client.subscriptions), 0)

    def test_close(self):
        # Acquire a subscription
        client_handler, token = self.test_acquire_subscription()
        
        # The client disconnects
        client_handler.on_close()

        # The subscription should not exist anymore
        with self.assertRaises(UnknownSubscription):
            self.sm.get_subscription_with_token(token)

    def test_bad_input_arguments(self):
        # Create test client handler
        client_handler = TestableFrontendHandler(self.facade)

        # The client connects
        client_handler.open()

        # The client does not provide enough parameters
        with ExpectLog('tornado.general', 
                'Frontend: 422 Unprocessable Entity'):
            client_handler.on_message(json.dumps({
                "call_id": 1,
                "function": "acquire_subscription",
            }))

        # They should have received an error message
        self.assertEqual(json.loads(client_handler._sent_message), {
            "type": "error",
            "call_id": 1,
            "status_code": 422,
            "reason": "Unprocessable Entity"
        })

    def test_bad_input_no_call(self):
        # Create test client handler
        client_handler = TestableFrontendHandler(self.facade)

        # The client connects
        client_handler.open()

        # The client does not provide a valid request
        with ExpectLog('tornado.general', 
                'Frontend: 422 Unprocessable Entity'):
            client_handler.on_message(json.dumps({
                "foo": "bar"
            }))

        # They should have received an error message, without the call_id
        self.assertEqual(json.loads(client_handler._sent_message), {
            "type": "error",
            "status_code": 422,
            "reason": "Unprocessable Entity"
        })

    def test_bad_json(self):
        # Create test client handler
        client_handler = TestableFrontendHandler(self.facade)

        # The client connects
        client_handler.open()

        # The client does not even provide a valid JSON
        with ExpectLog('tornado.general', 
                'Frontend: 400 Bad Request'):
            client_handler.on_message('{"foo":bar}')

        # They should have received an error message
        self.assertEqual(json.loads(client_handler._sent_message), {
            "type": "error",
            "status_code": 400,
            "reason": "Bad Request"
        })

    def test_receive_delta(self):
        client_handler, token = self.test_acquire_subscription()

        # Send a delta
        delta = Delta(created=[
            DeltaItemCreation('Player', {
                'id': 1,
                'name': 'Alice',
                'color': 'red'
            })
        ], updated=[], deleted=[])
        self.facade.deliver_delta(delta)

        self.assertEqual(json.loads(client_handler._sent_message), {
            "type": "delta",
            "created": [
                {
                    "model_class_name": "Player",
                    "data": {
                        "id": 1,
                        "name": "Alice",
                        "color": "red"
                    }
                }
            ],
            "updated": [],
            "deleted": []
        })
