from miau.common.types import MultiDict
import itertools

__all__ = ('UnknownDealer', 'UnknownModelClass', 'DealerManager')


class UnknownDealer(Exception):
    def __init__(self, dealer_name):
        self.dealer_name = dealer_name

    def __str__(self):
        return "No dealer named '%s'." % self.dealer_name


class UnknownModelClass(Exception):
    def __init__(self, dealer_name):
        self.dealer_name = dealer_name

    def __str__(self):
        return "No model class with name '%s' has been registered in the "\
                "dealer manager" % self.dealer_name


class DealerManager(object):
    """Tracks dealers registered in the system."""

    __slots__ = ('dealers_by_name', 'dealers_by_model_class')

    def __init__(self):
        self.dealers_by_name = {}
        self.dealers_by_model_class = MultiDict()

    def register_dealer(self, dealer):
        """Registers a new dealer."""
        name = dealer.name
        model = dealer.model

        if self.dealers_by_name.get(name):
            raise RuntimeError(
                    "Dealer with name '%s' already is registered." % name)

        # Add to dealers_by_name
        self.dealers_by_name[name] = dealer

        # Add to dealers_by_model_class
        self.dealers_by_model_class.add(model, dealer)

    def get_dealer(self, name):
        """Returns a dealer with the specified name"""
        try:
            return self.dealers_by_name[name]
        except KeyError:
            raise UnknownDealer(name)

    def get_dealers_for_model_class(self, model):
        """Returns an iterable of dealers with the specified model
        """
        try:
            return self.dealers_by_model_class[model]
        except KeyError:
            raise UnknownModelClass(model)

    def deliver_delta(self, delta, service):
        # Deliver to associated dealers
        for dealer in self.get_dealers_for_model_class(delta.model):
            dealer.deliver_delta(delta, service)

    def connect_subscription(self, subscription):
        for item in subscription.items:
            dealer = self.get_dealer(item.dealer_name)
            dealer.add_subscription_item(item)

    def disconnect_subscription(self, subscription):
        for item in subscription.items:
            dealer = self.get_dealer(item.dealer_name)
            dealer.remove_subscription_item(item)
