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
        self.dealers_by_model_class = {}
        
    def register_dealer(self, dealer):
        """Registers a new dealer."""
        name = dealer.name
        model_class_name = dealer.model_class_name

        if self.dealers_by_name.get(name):
            raise RuntimeError(
                    "Dealer with name '%s' already is registered." % name)

        # Add to dealers_by_name
        self.dealers_by_name[name] = dealer

        # Add to dealers_by_model_class
        same_class = self.dealers_by_model_class.setdefault(
                model_class_name, set())
        same_class.add(dealer)

    def get_dealer(self, name):
        """Returns a dealer with the specified name"""
        try:
            return self.dealers_by_name[name]
        except KeyError:
            raise UnknownDealer(name)

    def get_dealers_for_model_class(self, model_class_name):
        """Returns an iterable of dealers with the specified model_class_name
        """
        try:
            return self.dealers_by_model_class[model_class_name]
        except KeyError:
            raise UnknownModelClass(model_class_name)

    def deliver_delta(self, delta):
        # For each delta item
        for delta_item in itertools.chain(
                delta.created, delta.updated, delta.deleted):

            # Deliver to associated dealers
            model_class_name = delta_item.model_class_name

            for dealer in self.get_dealers_for_model_class(model_class_name):
                dealer.deliver_delta_item(delta_item)
