import simplejson as json

__all__ = ('Delta', 'DeltaItem', 'DeltaItemCreation', 'DeltaItemUpdate',
        'DeltaItemDeletion')


class Delta(object):
    """A collection of DeltaItemCreation's, DeltaItemUpdate's and
    DeltaItemDeletion's"""
    def __init__(self, created, updated, deleted):
        self.created = created
        self.updated = updated
        self.deleted = deleted

    def jsonify(self):
        """Encodes this delta as unicode-JSON."""
        return json.dumps(self, for_json=True, ensure_ascii=False)

    def for_json(self):
        """Returns this object's data as a JSON-serializable dictionary."""
        return {
            'created': self.created,
            'updated': self.updated,
            'deleted': self.deleted,
        }

        
class DeltaItem(object):
    """The base class for DeltaItemCreation, DeltaItemUpdate and
    DeltaItemDeletion"""
    def __init__(self, model_class_name):
        self.model_class_name = model_class_name


class DeltaItemCreation(DeltaItem):
    delta_type = 'creation'

    __slots__ = ('model_class_name', 'data')

    def __init__(self, model_class_name, data):
        self.model_class_name = model_class_name
        self.data = data

    def for_json(self):
        """Returns this object's data as a JSON-serializable dictionary."""
        return {
            'model_class_name': self.model_class_name,
            'data': self.data,
        }


class DeltaItemDeletion(DeltaItem):
    delta_type = 'deletion'

    __slots__ = ('model_class_name', 'data')

    def __init__(self, model_class_name, data):
        self.model_class_name = model_class_name
        self.data = data

    def for_json(self):
        """Returns this object's data as a JSON-serializable dictionary."""
        return {
            'model_class_name': self.model_class_name,
            'data': self.data,
        }


class DeltaItemUpdate(DeltaItem):
    delta_type = 'update'

    __slots__ = ('model_class_name', 'new_data', 'old_data')

    def __init__(self, model_class_name, old_data, new_data):
        self.model_class_name = model_class_name
        self.old_data = old_data
        self.new_data = new_data

    def for_json(self):
        """Returns this object's data as a JSON-serializable dictionary."""
        return {
            'model_class_name': self.model_class_name,
            'old_data': self.old_data,
            'new_data': self.new_data,
        }
