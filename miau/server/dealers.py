import abc
from miau.common.delta import Delta, DeltaItem, DeltaItemCreation, \
        DeltaItemUpdate, DeltaItemDeletion

__all__ = ('Dealer', 'BroadcastDealer', 'SimpleDealer')


class Dealer(object):
    __metaclass__ = abc.ABCMeta
    __slots__ = tuple()

    @property
    def name(self):
        return self.__class__.__name__

    @abc.abstractmethod
    def add_subscription_item(self, item): pass

    @abc.abstractmethod
    def remove_subscription_item(self, item): pass

    @abc.abstractmethod
    def get_subscription_items_for_model(self, model): pass

    def deliver_delta_item(self, delta_item):
        """Receives a delta_item, computes a set of destination subscriptions
        items and forwards the delta to them.
        
        Please note that altough DeltaItemCreation and DeltaItemDeletion will
        always trigger deltas of the same time on the client, DeltaItemUpdate
        may not. To understand this fact, see the next example:
        
        Suppose our model class composes a player name and a color, i.e.
        'id: 1, name: Alice, color: blue'.
        
        We may also have a dealer named 'Players with color' that uses the
        `color` attribute to filter players.
        
        A client maybe subscripted to players with color red, showing them in a
        list. Now, if Alice changes its color to red, this client will receive
        a creation delta instead of an update one because they had no previous
        knowledge of Alice's model and will have to render it as a new row. 
        
        If then Alice decides to change her player name, the client will
        receive a delta update because they already knew Alice's model.
        
        And lastly, if Alice changes its color again to other than red the new
        model will no longer satisfy the filter and thus a deletion delta will
        be sent to the client.
        """

        if delta_item.delta_type != 'update':
            # If origin delta is creation or deletion
            model_data = delta_item.data
            deliver_to = self.get_subscription_items_for_model(model_data)

            delta = {
                'creation': lambda item: Delta([item], [], []),
                'deletion': lambda item: Delta([], [], [item])
            }[delta_item.delta_type](delta_item)

            for subscription_item in deliver_to:
                subscription_item.deliver_delta(delta)

        else:
            # If origin delta is an update
            model_class_name = delta_item.model_class_name
            new_data = delta_item.new_data
            old_data = delta_item.old_data

            set_old = self.get_subscription_items_for_model(old_data)
            set_new = self.get_subscription_items_for_model(new_data)

            # Prepare every type of destination delta
            creation_delta = Delta([
                DeltaItemCreation(model_class_name, new_data)
            ], [], [])
            update_delta = Delta([], [
                DeltaItemUpdate(model_class_name, old_data, new_data)
            ], [])
            deletion_delta = Delta([], [], [
                DeltaItemDeletion(model_class_name, old_data)
            ])

            # For the subscription items that do not match the filter with the
            # old data but do with the new data, send a creation delta.
            for subscription_item in set_new - set_old:
                subscription_item.deliver_delta(creation_delta)

            # For the subscription items that match the filter with both the
            # new and old data, send an update delta.
            for subscription_item in set_old.intersection(set_new):
                subscription_item.deliver_delta(update_delta)

            # For the subscription items that match the filter with the old
            # data but do not match with the new data, send a deletion delta.
            for subscription_item in set_old - set_new:
                subscription_item.deliver_delta(deletion_delta)


class BroadcastDealer(Dealer):
    name = 'broadcast'
    __slots__ = ('items',)

    def __init__(self):
        super(BroadcastDealer, self).__init__()
        self.items = set()

    def add_subscription_item(self, item):
        self.items.add(item)

    def remove_subscription_item(self, item):
        self.items.remove(item)

    def get_subscription_items_for_model(self, model):
        return self.items


class SimpleDealer(Dealer):
    __slots__ = ('items_by_model_key',)

    def __init__(self):
        super(SimpleDealer, self).__init__()
        self.items_by_model_key = dict()

    @abc.abstractmethod
    def get_key_for_model(self, model): pass

    def add_subscription_item(self, item):
        model_key = item.model_key

        # Get the set of items with the same model_key or create one if there
        # are no one yet.
        items_with_this_key = self.items_by_model_key.setdefault(
                model_key, set())
        # Add this item to the set.
        items_with_this_key.add(item)

    def remove_subscription_item(self, item):
        # Remove item from the set of items with the same model_key.
        items_with_key = self.items_by_model_key[item.model_key]
        items_with_key.remove(item)

        # Delete the set of items with the same model_key if now it's empty.
        if len(items_with_key) == 0:
            del self.items_by_model_key[item.model_key]

    def get_subscription_items_for_model(self, model):
        model_key = self.get_key_for_model(model)

        # Return the set of items with this model_key, or an empty set if
        # there is none.
        return self.items_by_model_key.get(model_key, set())
