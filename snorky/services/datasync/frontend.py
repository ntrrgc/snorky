from snorky.services.base import RPCService, RPCError, rpc_command
from snorky.services.datasync.managers.dealer import DealerManager
from snorky.services.datasync.managers.subscription import SubscriptionManager
from miau.common.types import is_string


class DataSyncService(RPCService):
    def __init__(self, name):
        super(DataSyncService, self).__init__(name)

        self.dm = DealerManager()
        self.sm = SubscriptionManager()

    @rpc_command
    def acquire_subscription(self, req, token):
        if not is_string(token):
            raise RPCError("token must be string")

        subscription = self.sm.get_subscription_with_token(token)
        if not subscription:
            raise RPCError("No such subscription")

        self.sm.link_subscription_to_client(subscription, req.client)

    @rpc_command
    def cancel_subscription(self, req, token):
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
        for subscription in list(self.sm.subscriptions_by_client[client]):
            self.do_cancel_subscription(subscription)

