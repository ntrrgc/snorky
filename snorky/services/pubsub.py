# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from snorky.services.base import RPCService, RPCError, rpc_command
from snorky.types import MultiDict


class PubSubService(RPCService):
    """A service which allows clients to send messages to each other over Pub
    Sub channels."""
    def __init__(self, name):
        super(PubSubService, self).__init__(name)

        # channel : str -> set<Client>
        self.subscriptions = MultiDict()
        # Client -> set<channel : str>
        self.subscriptions_by_client = MultiDict()

    def do_publish(self, channel, message):
        """Common code for publishing a message."""
        for client in self.subscriptions.get_set(channel):
            self.send_message_to(client, {
                "type": "message",
                "channel": channel,
                "message": message
            })

    @rpc_command
    def publish(self, req, channel, message):
        """RPC command.

        Publish a message to a channel."""
        if self.can_publish(req.client, channel):
            self.do_publish(channel, message)
        else:
            raise RPCError("Not authorized")

    @rpc_command
    def subscribe(self, req, channel):
        """RPC command.

        Subscribe to a channel."""
        if self.subscriptions.in_set(channel, req.client):
            raise RPCError("Already subscribed")
        self.subscriptions.add(channel, req.client)
        self.subscriptions_by_client.add(req.client, channel)

    @rpc_command
    def unsubscribe(self, req, channel):
        """RPC command.

        Cancel the subscription to a channel."""
        try:
            self.subscriptions.remove(channel, req.client)
            self.subscriptions_by_client.remove(req.client, channel)
        except KeyError:
            raise RPCError("Not subscribed")

    def can_publish(self, client, channel):
        """Whether a client can publish to a certain channel.

        By default returns always ``True``."""
        return True

    def client_disconnected(self, client):
        """Exececuted when a client disconnects. Cancels all its subscriptions.
        """
        for channel in self.subscriptions_by_client.get_set(client):
            self.subscriptions.remove(channel, client)
        self.subscriptions_by_client.clear_set(client)


class PubSubBackend(RPCService):
    """Backend service which allows publishing to a Pub Sub service.

    :param frontend: The :class:`PubSubService` instance messages will
                     be published to.

    Publishing from this backend will always be allowed regardless of the
    policies implemented in :meth:`PubSubService.can_publish`."""
    def __init__(self, name, frontend):
        """"""
        super(PubSubBackend, self).__init__(name)
        self.frontend = frontend

    @rpc_command
    def publish(self, req, channel, message):
        """RPC command.

        Publish a message to a channel."""
        self.frontend.do_publish(channel, message)
