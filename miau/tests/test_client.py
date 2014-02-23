import unittest
import miau.server.client
import miau.common.delta


class FakeInnerClient(object):
    def __init__(self):
        self.message = None

    def write_message(self, message):
        self.message = message


class FakeSubscription(object):
    def __init__(self, token):
        self.token = token
        self.client = None

    def got_client(self, client):
        if self.client is None:
            self.client = client
        else:
            raise RuntimeError('Subscription already owned')

    def lost_client(self):
        if self.client is not None:
            self.client = None
        else:
            raise RuntimeError('Subscription not owned')


class TestClient(unittest.TestCase):
    def setUp(self):
        self.inner_client = FakeInnerClient()

    def test_write_message(self):
        client = miau.server.client.Client(self.inner_client)

        # Assert no message sent yet
        self.assertIsNone(self.inner_client.message)

        # Send hello
        client.write_message('Hello')
        self.assertEqual(self.inner_client.message, 'Hello')

    def test_link_subscription(self):
        client = miau.server.client.Client(self.inner_client)

        # Link
        subscription = FakeSubscription(1)
        client.link_subscription(subscription)

        self.assertIs(subscription.client, client)
        self.assertIn(subscription, client.subscriptions)

        # Unlink
        client.unlink_subscription(subscription)

        self.assertIsNone(subscription.client)
        self.assertNotIn(subscription, client.subscriptions)


if __name__ == "__main__":
    unittest.main()
