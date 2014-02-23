import unittest
from miau.server.managers.dealer import DealerManager, UnknownModelClass, \
        UnknownDealer
from miau.common.delta import Delta, DeltaItem, DeltaItemCreation, \
        DeltaItemUpdate, DeltaItemDeletion


class FakeDealer(object):
    def __init__(self, name, model_class_name, deliver_delta_item):
        self.name = name
        self.model_class_name = model_class_name

        self.deliver_delta_item = deliver_delta_item

class TestDealerManager(unittest.TestCase):
    def setUp(self):
        def deliver_delta_item(delta_item):
            self._delta_item = delta_item
        self._delta_item = None

        self.dealer1 = FakeDealer('test_dealer1', 'test_model', 
                deliver_delta_item)
        self.dealer2 = FakeDealer('test_dealer2', 'test_model', 
                deliver_delta_item)
    
    def test_register_dealer(self):
        dm = DealerManager()

        # Register a dealer
        dm.register_dealer(self.dealer1)
        self.assertIs(dm.get_dealer('test_dealer1'), self.dealer1)
        self.assertEqual(set(dm.get_dealers_for_model_class('test_model')),
                {self.dealer1})

        # Register a second dealer for the same model class
        dm.register_dealer(self.dealer2)
        self.assertIs(dm.get_dealer('test_dealer2'), self.dealer2)
        self.assertEqual(set(dm.get_dealers_for_model_class('test_model')),
                {self.dealer1, self.dealer2})

    def test_get_unregistered_dealer(self):
        dm = DealerManager()

        with self.assertRaises(UnknownDealer):
            dm.get_dealer('foo')

    def test_deliver_delta(self):
        dm = DealerManager()
        dm.register_dealer(self.dealer1)

        # Send a delta of the same model class of the registered dealer
        delta_creation = DeltaItemCreation('test_model', {'id':1})
        delta = Delta(created=[delta_creation], updated=[], deleted=[])
        dm.deliver_delta(delta)

        self.assertIs(self._delta_item, delta_creation)

    def test_deliver_delta_without_dealer(self):
        dm = DealerManager()

        # Send a delta of a model class without dealers
        delta_creation = DeltaItemCreation('test_model', {'id':1})
        delta = Delta(created=[delta_creation], updated=[], deleted=[])

        with self.assertRaises(UnknownModelClass):
            dm.deliver_delta(delta)

    def test_deliver_delta_other_model_class(self):
        dm = DealerManager()
        dm.register_dealer(self.dealer1)

        # Send a delta of a model class without dealers
        delta_creation = DeltaItemCreation('unknown_model', {'id':1})
        delta = Delta(created=[delta_creation], updated=[], deleted=[])

        with self.assertRaises(UnknownModelClass):
            dm.deliver_delta(delta)
