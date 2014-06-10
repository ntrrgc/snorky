__all__ = ('Subscription', 'SubscriptionItem')


class Subscription(object):
    """
    An object which represents a contract that may be signed by a Client to be
    notified by one or more dealers, providing one or more model keys for each
    Dealer.

    Each pair of Dealer and model_key is stored as a SubscriptionItem.

    A Subscription distinguishes three states:

    * Acquired: A Client has been associated with the Subscription (in other
      words, it has signed the contract). In order for a client to acquire a
      Subscription it needs to know its subscription_token.

    * WaitingClient: No client has acquired the Subscription yet. The
      Subscription object will store any deltas for the subscription items and
      forward them to the Client when it acquires the Subscription.

    * Stale: Time has passed since the Subscription was created but no Client
      has acquired it. Subscriptions in this state will be removed by the
      system in order to free memory.
    """

    __slots__ = ('token', 'client', 'attached', '_awaited_client_buffer',
            '_awaited_client_timeout', 'items')

    def __init__(self, items):
        self.token = None
        self.client = None
        self.attached = False
        self._awaited_client_buffer = []

        self.items = items
        for item in items:
            item.subscription = self

    @property
    def acquired(self):
        return self.client is not None

    def got_client(self, client):
        """Links this subscription with a client. If there were deltas received
        before, they will be sent now."""

        if self.client is not None:
            raise RuntimeError("Subscription already linked to a Client")

        self.client = client
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
            self.client.deliver_delta(delta)
        else:
            self._awaited_client_buffer.append(delta)

    def flush_awaited_client_buffer(self):
        """Sends deltas stored in the _awaited_client_buffer to the client and
        clears the buffer."""

        for delta in self._awaited_client_buffer:
            self.deliver_delta(delta)

        # Clear buffer
        self._awaited_client_buffer[:] = []

    def attach_to_dealers(self, dealer_manager):
        """Registers each subscription item in its associated dealer."""
        if self.attached:
            raise RuntimeError("Already attached.")

        for item in self.items:
            dealer = dealer_manager.get_dealer(item.dealer_name)
            dealer.add_subscription_item(item)

        self.attached = True

    def dettach_from_dealers(self, dealer_manager):
        """Unregisters each subscription item in its associated dealer."""
        if not self.attached:
            raise RuntimeError("Not attached.")

        for item in self.items:
            dealer = dealer_manager.get_dealer(item.dealer_name)
            dealer.remove_subscription_item(item)

        self.attached = False

    def cancel_timeout(self, io_loop):
        io_loop.remove_timeout(self._awaited_client_timeout)
        self._awaited_client_timeout = None


class SubscriptionItem(object):
    """A pair of dealer_name and model_key linked to a Subscription."""

    __slots__ = ('dealer_name', 'model_key', 'subscription')

    def __init__(self, dealer_name, model_key, subscription=None):
        self.dealer_name = dealer_name
        self.model_key = model_key
        self.subscription = subscription

    def deliver_delta(self, delta):
        """Delivers a delta to its associated Subscription object"""
        self.subscription.deliver_delta(delta)
