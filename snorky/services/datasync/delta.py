# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class Delta(object):
    """Any kind of data change notification."""
    __slots__ = tuple()

    def __eq__(self, other):
        # Only used in unit tests
        return isinstance(other, Delta) and self.for_json() == other.for_json()


class InsertionDelta(Delta):
    """An insertion notification."""
    __slots__ = ("model", "data")

    def __init__(self, model, data):
        self.model = model
        """The model class name this change occured in."""

        self.data = data
        """The inserted data."""

    def for_json(self):
        """Returns this instance as a dictionary."""
        return {
            "type": "insert",
            "model": self.model,
            "data": self.data,
        }


class UpdateDelta(Delta):
    """An update notification."""
    __slots__ = ("model", "new_data", "old_data")

    def __init__(self, model, new_data, old_data):
        self.model = model
        """The model class name this change occured in."""

        self.new_data = new_data
        """The updated data."""

        self.old_data = old_data
        """The data before the update."""

    def for_json(self):
        """Returns this instance as a dictionary."""
        return {
            "type": "update",
            "model": self.model,
            "newData": self.new_data,
            "oldData": self.old_data,
        }


class DeletionDelta(Delta):
    """A deletion notification."""
    __slots__ = ("model", "data")

    def __init__(self, model, data):
        self.model = model
        """The model class name this change occured in."""

        self.data = data
        """The updated data."""

    def for_json(self):
        """Returns this instance as a dictionary."""
        return {
            "type": "delete",
            "model": self.model,
            "data": self.data,
        }
