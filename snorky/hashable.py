# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class HashableList(list):
    """A :class:`list` subclass with a :meth:`__hash__` method, therefore
    allowing it to be used as key in a dictionary.

    The hash will be static once it is computed, even if items of the list are
    edited. Please abstain from doing so.
    """
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self._hash = None

    def __hash__(self):
        if not self._hash:
            self._hash = hash(tuple(self))
        return self._hash


class HashableDict(dict):
    """A :class:`dict` subclass with a :meth:`__hash__` method, therefore
    allowing it to be used as key in a dictionary.

    The hash will be static once it is computed, even if items of the
    dictionary are edited. Please abstain from doing so.
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._hash = None

    def __hash__(self):
        if not self._hash:
            self._hash = hash(tuple(sorted(self.items())))
        return self._hash


def make_hashable(json_object):
    """Recursively transform a JSON decoded entity into a hashable one,
    substituting all appearances of :class:`list` with :class:`HashableList`
    and all appearances of :class:`dict` with :class:`HashableDict`. Other data
    types are kept unchanged.

    Returns a hashable JSON entity.
    """
    if isinstance(json_object, dict):
        return HashableDict(
            (key, make_hashable(value))
            for (key, value) in json_object.items()
        )
    elif isinstance(json_object, list):
        return HashableList(make_hashable(x)
                            for x in json_object)
    else:
        return json_object
