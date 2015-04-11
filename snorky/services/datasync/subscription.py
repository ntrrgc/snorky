# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

__all__ = ('Subscription', 'SubscriptionItem')


class SubscriptionItem(object):
    """A pair of dealer_name and query linked to a Subscription."""

    __slots__ = ('dealer_name', 'query', 'subscription')

    def __init__(self, dealer_name, query, subscription=None):
        self.dealer_name = dealer_name
        self.query = query
        self.subscription = subscription


class Subscription(object):
    """
    An object which represents a contract that may be signed by a Client to be
    notified by one or more dealers, providing one or more queries for each
    Dealer.

    Each pair of Dealer and query is stored as a SubscriptionItem.

    A Subscription distinguishes three states:

    * Acquired: A Client has been associated with the Subscription (in other
      words, it has signed the contract). In order for a client to acquire a
      Subscription it needs to know its subscription_token.

    * Awaiting client: No client has acquired the Subscription yet. The
      Subscription object will store any deltas for the subscription items and
      forward them to the Client when it acquires the Subscription.

    * Stale: Time has passed since the Subscription was created but no Client
      has acquired it. Subscriptions in this state will be removed by the
      system in order to free memory.
    """

    __slots__ = ('token', 'client', '_awaited_client_buffer',
            '_awaited_client_timeout', 'items', 'service')

    def __init__(self, items, service):
        self.token = None
        self.client = None
        self._awaited_client_buffer = []
        self._awaited_client_timeout = None

        self.service = service
        self.items = items
        for item in items:
            item.subscription = self

    def got_client(self, client):
        """Links this subscription with a client. If there were deltas received
        before, they will be sent now."""

        if self.client is not None:
            raise RuntimeError("Subscription already linked to a Client")

        self.client = client
        self.cancel_timeout()
        self.flush_awaited_client_buffer()

    def lost_client(self):
        """Unlinks this subscription from its client. New arrived deltas will
        no further be delivered to it."""

        self.client = None

    def deliver_delta(self, delta):
        """Sends a JSON encoded delta to the associated client.

        If there is currently no associated client the delta will be stored to
        be sent when a client arrives."""

        if self.client is not None:
            self.service.deliver_delta(self.client, delta)
        else:
            self._awaited_client_buffer.append(delta)

    def flush_awaited_client_buffer(self):
        """Sends deltas stored in the _awaited_client_buffer to the client and
        clears the buffer."""

        for delta in self._awaited_client_buffer:
            self.deliver_delta(delta)

        # Clear buffer
        self._awaited_client_buffer[:] = []

    def cancel_timeout(self):
        if self._awaited_client_timeout:
            self._awaited_client_timeout.cancel()
            self._awaited_client_timeout = None
