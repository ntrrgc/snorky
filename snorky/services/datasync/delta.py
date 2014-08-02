class Delta(object):
    __slots__ = tuple()

    def __eq__(self, other):
        # Only used in unit tests
        return isinstance(other, Delta) and self.for_json() == other.for_json()


class InsertionDelta(Delta):
    __slots__ = ("model", "data")

    def __init__(self, model, data):
        self.model = model
        self.data = data

    def for_json(self):
        return {
            "type": "insert",
            "model": self.model,
            "data": self.data,
        }


class UpdateDelta(Delta):
    __slots__ = ("model", "new_data", "old_data")

    def __init__(self, model, new_data, old_data):
        self.model = model
        self.new_data = new_data
        self.old_data = old_data

    def for_json(self):
        return {
            "type": "update",
            "model": self.model,
            "newData": self.new_data,
            "oldData": self.old_data,
        }


class DeletionDelta(Delta):
    __slots__ = ("model", "data")

    def __init__(self, model, data):
        self.model = model
        self.data = data

    def for_json(self):
        return {
            "type": "delete",
            "model": self.model,
            "data": self.data,
        }
