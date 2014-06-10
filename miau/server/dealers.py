import abc
from collections import namedtuple
from functools import wraps
from miau.common.types import PY2, StringTypes, Number
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


FilterAssociation = namedtuple('FilterAssociation',
                               ('filter', 'subscription_item'))

"""
Filter syntax
=============

['=', 'color', 'blue']
color is 'blue'

['<', 'age', 21]
age is less than 21

['>=', 'age', 21]
age is greater than or equal to 21

['and', ['=', 'service', 'prosody'], ['>=', 'severity_level', 3]]
service is 'prosody' and severity_level is greater than or equal to 3

['or', ['not', ['=', 'service', 'java']], ['>=', 'severity_level', 3]]
service is not 'java' or severity_level is greater than or equal to 3

['=', 'player.color', 'blue']
color of player is 'blue'
"""

def get_field(model, name):
    """
    Given a dictionary for `model` and a dot separated string for `name`,
    accesses the named properties in model.

    e.g. get_field(model, 'service.name') returns model['service']['name']
    """
    prop = model
    for prop_name in name.split('.'):
        prop = model[prop_name]
    return prop

def false_on_raise(function):
    @wraps(function)
    def _false_on_raise(*args):
        try:
            return function(*args)
        except (KeyError, TypeError):
            # KeyError: missing property
            # TypeError: unorderable types (e.g. compared str with int)
            return False
    return _false_on_raise

def orderable_types(a, b):
    return (isinstance(a, Number) and isinstance(b, Number)) or \
            (isinstance(a, StringTypes) and isinstance(b, StringTypes))

@false_on_raise
def filter_eq(model, field, value):
    return get_field(model, field) == value

@false_on_raise
def filter_lt(model, field, value):
    field_value = get_field(model, field)
    # Python3 does not allow to compare strings with numbers, emulate that.
    if PY2 and not orderable_types(field_value, value):
        raise TypeError
    return field_value < value

@false_on_raise
def filter_lte(model, field, value):
    field_value = get_field(model, field)
    # Python3 does not allow to compare strings with numbers, emulate that.
    if PY2 and not orderable_types(field_value, value):
        raise TypeError
    return field_value <= value

@false_on_raise
def filter_gt(model, field, value):
    field_value = get_field(model, field)
    # Python3 does not allow to compare strings with numbers, emulate that.
    if PY2 and not orderable_types(field_value, value):
        raise TypeError
    return field_value > value

@false_on_raise
def filter_gte(model, field, value):
    field_value = get_field(model, field)
    # Python3 does not allow to compare strings with numbers, emulate that.
    if PY2 and not orderable_types(field_value, value):
        raise TypeError
    return field_value >= value

@false_on_raise
def filter_not(model, expr):
    return not filter_matches(model, expr)

@false_on_raise
def filter_and(model, *expressions):
    return all(filter_matches(model, expr)
               for expr in expressions)

@false_on_raise
def filter_or(model, *expressions):
    return any(filter_matches(model, expr)
               for expr in expressions)

operator_functions = {
    '==': filter_eq,
    '<': filter_lt,
    '<=': filter_lte,
    '>': filter_gt,
    '>=': filter_gte,
    'and': filter_and,
    'or': filter_or,
    'not': filter_not,
}

def filter_matches(model, filter):
    op = filter[0]
    args = filter[1:]
    return operator_functions[op](model, *args)

class FilterDealer(Dealer):
    __slots__ = ('filters',)

    def __init__(self):
        super(FilterDealer, self).__init__()
        self.filters = {}

    def add_subscription_item(self, item):
        filter = item.model_key
        self.filters[item] = filter

    def remove_subscription_item(self, item):
        self.filters.remove(item)

    def get_subscription_items_for_model(self, model):
        for subs_item, filter in self.filters.items():
            if filter_matches(filter, model):
                yield subs_item
