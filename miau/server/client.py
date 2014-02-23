import simplejson as json

__all__ = ('Client',)


class Client(object):
    """Encapsulates a websocket connection."""

    __slots__ = ('inner_client', 'subscriptions')

    def __init__(self, inner_client):
        self.inner_client = inner_client
        self.subscriptions = set()

    def write_message(self, message):
        """Sends a message through a websocket connection"""
        self.inner_client.write_message(message)

    def link_subscription(self, subscription):
        """Tells a Subscription object this is its new client and adds the
        Subscription object to the `subscriptions` set."""

        subscription.got_client(self)
        self.subscriptions.add(subscription)

    def unlink_subscription(self, subscription):
        """Removes a Subscription from the `subscriptions` set and tells the
        Subscription object this Client is not associated with it anymore.

        Note: This function does not destroy the Subscription object nor
        prevents it from receiving deltas from dealers. See
        `miau.server.facade.FrontendFacade.cancel_subscription` for that."""

        self.subscriptions.remove(subscription)
        subscription.lost_client()

    def deliver_delta(self, delta):
        """Encodes a delta as JSON and sends it to the user.
        Adds a 'type' field which is helpful for the client in order to tell
        apart this delta from a function response or other kind of message."""

        data = delta.for_json()
        data['type'] = 'delta'

        self.write_message(json.dumps(data, for_json=True, ensure_ascii=False))
