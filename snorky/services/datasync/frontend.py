from snorky.services.base import RPCService, RPCError, rpc_command
from snorky.services.datasync.managers.dealer import DealerManager
from snorky.services.datasync.managers.subscription import SubscriptionManager
from snorky.types import is_string


class DataSyncService(RPCService):
    def __init__(self, name, dealers=[]):
        super(DataSyncService, self).__init__(name)

        self.dm = DealerManager()
        self.sm = SubscriptionManager()

        for dealer in dealers:
            self.register_dealer(dealer)

    def register_dealer(self, dealer):
        # Accept both a Dealer class or a Dealer instance.
        # If it receives a class, instantiate it.
        if isinstance(dealer, type):
            instance = dealer()
        else:
            instance = dealer

        self.dm.register_dealer(instance)
        return instance

    def unregister_dealer(self, dealer):
        # Note unregister_dealer only accepts an instance, not a class.
        # There could be several instances of the same Dealer class.

        # Note also this method does not do any cleaning of subscriptions,
        # therefore it should only be called before there are any clients
        # connected.
        self.dm.unregister_dealer(dealer)

    @rpc_command
    def acquireSubscription(self, req, token):
        if not is_string(token):
            raise RPCError("token must be string")

        subscription = self.sm.get_subscription_with_token(token)
        if not subscription:
            raise RPCError("No such subscription")

        self.sm.link_subscription_to_client(subscription, req.client)

    @rpc_command
    def cancelSubscription(self, req, token):
        if not is_string(token):
            raise RPCError("token must be string")

        subscription = self.sm.get_subscription_with_token(token)
        if not subscription or subscription.client is not req.client:
            raise RPCError("No such subscription")

        self.do_cancel_subscription(subscription)

    def do_cancel_subscription(self, subscription):
        self.dm.disconnect_subscription(subscription)

        if subscription.client is not None:
            self.sm.unlink_subscription_from_client(subscription)

        self.sm.unregister_subscription(subscription)

    def deliver_delta(self, client, delta):
        self.send_message_to(client, {
            "type": "delta",
            "delta": delta.for_json()
        })

    def client_disconnected(self, client):
        subscriptions = list(self.sm.subscriptions_by_client.get_set(client))
        for subscription in subscriptions:
            self.do_cancel_subscription(subscription)

