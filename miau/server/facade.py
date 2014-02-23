import datetime
from tornado.ioloop import IOLoop
from miau.server.subscription import Subscription

CLIENT_ARRIVAL_TIMEOUT = datetime.timedelta(seconds=300)

class Facade(object):
    """Provides a simple interface to perform common operations."""

    def __init__(self, dealer_manager, subscription_manager, io_loop):
        self.dm = dealer_manager
        self.sm = subscription_manager
        self.io_loop = io_loop

    def authorize_subscription(self, items):
        subscription = Subscription(items)

        token = self.sm.register_subscription(subscription)

        subscription.attach_to_dealers(self.dm)

        callback = self.sm.get_subscription_timeout_callback(subscription)
        timeout = self.io_loop.add_timeout(
                CLIENT_ARRIVAL_TIMEOUT, callback)
        subscription._awaited_client_timeout = timeout

        return token

    def acquire_subscription(self, client, token):
        subscription = self.sm.get_subscription_with_token(token)
        client.link_subscription(subscription)

        subscription.cancel_timeout(self.io_loop)

    def cancel_subscription(self, client, token):
        subscription = self.sm.get_subscription_with_token(token)

        # Makes client forget about this subscription
        client.unlink_subscription(subscription)

        # Tells dealers to stop delivering deltas of this subscription
        subscription.dettach_from_dealers(self.dm)

        # Makes SubscriptionManager forget about this subscription and its
        # token
        self.sm.unregister_subscription(subscription)

    def client_disconnected(self, client):
        # list() is needed in order to copy the `subscriptions` set. Otherwise
        # the iterator would break as soon as a subscription is removed in the
        # following line.
        for subscription in list(client.subscriptions):
            self.cancel_subscription(client, subscription.token)

    def deliver_delta(self, delta):
        return self.dm.deliver_delta(delta)
