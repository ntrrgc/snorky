import base64
import simplejson as json
from miau.server.managers.dealer import DealerManager
from miau.server.managers.subscription import SubscriptionManager, \
        UnknownSubscription
from miau.server.facade import Facade
from miau.server.backend import Backend
from miau.server.dealers import SimpleDealer
from tornado.testing import AsyncHTTPTestCase, ExpectLog


def build_auth(username, password):
    return b'Basic ' + base64.encodestring(password.encode() + b':')

json_headers = {
    'Content-Type': 'application/json; charset=UTF-8',
    'Accept': 'application/json; charset=UTF-8',
}


class PlayersWithColor(SimpleDealer):
    name = 'players_with_color'
    model_class_name = 'Player'
    
    def get_key_for_model(self, model):
        return model['color']


class TestBackend(AsyncHTTPTestCase):
    def setUp(self):
        self.dm = DealerManager()
        self.sm = SubscriptionManager()

        # Add a Dealer
        dealer = PlayersWithColor()
        self.dm.register_dealer(dealer)

        self.key = "Here_goes_a_super_secret_key"

        super(TestBackend, self).setUp()

    def get_app(self):
        # Facade has to be created here because self.io_loop does not exist
        # until parent's setUp() has been called, and parent's setUp() calls
        # get_app, which needs the Facade.
        if not hasattr(self, "facade"):
            self.facade = Facade(self.dm, self.sm, self.io_loop)

        return Backend(self.facade, self.key)

    def tearDown(self):
        del self.facade
        super(TestBackend, self).tearDown()

    def test_bad_request(self):
        raw_body = "Hello, World"

        with ExpectLog('tornado.access', '400 POST'):
            with ExpectLog('tornado.general', '.* Invalid syntax'):
                response = self.fetch('/subscription',
                    auth_username=self.key,
                    method="POST",
                    headers=json_headers,
                    body=raw_body)

        self.assertEqual(response.code, 400)
        self.assertIn(('Content-Type', 'application/json; charset=UTF-8'),
                response.headers.items())
        self.assertEqual(json.loads(response.body), {
            'status_code': 400,
            'reason': 'Bad Request'
        })

    def test_unprocessable_entity(self):
        body = {"foo": "bar"}

        with ExpectLog('tornado.access', '422 POST'):
            with ExpectLog('tornado.general', '.* Unprocessable entity'):
                response = self.fetch('/subscription',
                    auth_username=self.key,
                    method="POST",
                    headers=json_headers,
                    body=json.dumps(body))

        self.assertEqual(response.code, 422)

    def test_authorize_subscription(self):
        body = {
            "items": [
                {
                    "dealer_name": "players_with_color",
                    "model_key": "red"
                }
            ]
        }

        response = self.fetch('/subscription',
                auth_username=self.key,
                method="POST",
                headers=json_headers,
                body=json.dumps(body))

        self.assertEqual(response.code, 201)
        self.assertIn(('Content-Type', 'application/json; charset=UTF-8'),
                response.headers.items())

        r = json.loads(response.body, encoding="UTF-8")
        token = r["token"]

        # Assert the subscription has been created
        self.sm.get_subscription_with_token(token)

        return token

    def test_authorize_subscription_bad_key(self):
        body = {
            "items": [
                {
                    "dealer_name": "players_with_color",
                    "model_key": "red"
                }
            ]
        }

        with ExpectLog('tornado.access', '401 POST'):
            with ExpectLog('tornado.general', '.*Unauthorized'):
                response = self.fetch('/subscription',
                        auth_username='foo',
                        method="POST",
                        headers=json_headers,
                        body=json.dumps(body))

        self.assertEqual(response.code, 401)
        self.assertIn(('Content-Type', 'application/json; charset=UTF-8'),
                response.headers.items())

        r = json.loads(response.body, encoding="UTF-8")
        self.assertEqual(r, {
            'status_code': 401,
            'reason': 'Unauthorized',
        })

        # Assert no subscription has been created
        self.assertEqual(len(self.sm.subscriptions_by_token), 0)

    def test_authorize_subscription_unknown_dealer(self):
        body = {
            "items": [
                {
                    "dealer_name": "foo",
                    "model_key": "red"
                }
            ]
        }

        with ExpectLog('tornado.access', '422 POST'):
            with ExpectLog('tornado.general', '.*Unprocessable entity'):
                response = self.fetch('/subscription',
                        auth_username=self.key,
                        method="POST",
                        headers=json_headers,
                        body=json.dumps(body))

        self.assertEqual(response.code, 422)
        self.assertIn(('Content-Type', 'application/json; charset=UTF-8'),
                response.headers.items())

        r = json.loads(response.body, encoding="UTF-8")
        self.assertIn("Unknown dealer: foo", r["details"])

    def test_notify_delta(self):
        body = {
            "created": [
                {
                    "model_class_name": "Player",
                    "data": {
                        "id": 3,
                        "name": "Steve",
                        "color": "red"
                    }
                },
                {
                    "model_class_name": "Player",
                    "data": {
                        "id": 3,
                        "name": "Clarissa",
                        "color": "green"
                    }
                }
            ],
            "updated": [
                {
                    "model_class_name": "Player",
                    "old_data": {
                        "id": 2,
                        "name": "Alice",
                        "color": "blue"
                    },
                    "new_data": {
                        "id": 2,
                        "name": "Alice",
                        "color": "red"
                    }
                }
            ],
            "deleted": [
                {
                    "model_class_name": "Player",
                    "data": {
                        "id": 2,
                        "name": "Bob",
                        "color": "red"
                    }
                }
            ]
        }

        response = self.fetch('/notify_delta',
                auth_username=self.key,
                method="POST",
                headers=json_headers,
                body=json.dumps(body))

        self.assertEqual(response.code, 204)

    def test_notify_delta_malformed1(self):
        body = {
            "created": { #should be a list
                "model_class_name": "Player",
                "data": {
                    "id": 3,
                    "name": "Steve",
                    "color": "green"
                }
            },
            "updated": [],
            "deleted": []
        }
            
        with ExpectLog('tornado.access', '422 POST'):
            with ExpectLog('tornado.general', '.* Unprocessable entity'):
                response = self.fetch('/notify_delta',
                        auth_username=self.key,
                        method="POST",
                        headers=json_headers,
                        body=json.dumps(body))

        self.assertEqual(response.code, 422)

    def test_notify_delta_malformed2(self):
        body = {
            "created": [{
                "model_class_name": {"foo": "bar"},
                "data": {
                    "id": "3",
                    "name": "Steve",
                    "color": "green"
                }
            }],
            "updated": [],
            "deleted": []
        }
            
        with ExpectLog('tornado.access', '422 POST'):
            with ExpectLog('tornado.general', '.* Unprocessable entity'):
                response = self.fetch('/notify_delta',
                        auth_username=self.key,
                        method="POST",
                        headers=json_headers,
                        body=json.dumps(body))

        self.assertEqual(response.code, 422)

    def test_authorize_then_notify(self):
        token = self.test_authorize_subscription()
        self.test_notify_delta()

        # Assert deltas has been stored
        self.assertEqual(
                len(self.sm.get_subscription_with_token(token).
                _awaited_client_buffer), 3)
