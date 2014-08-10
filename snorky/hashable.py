class HashableList(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self._hash = None

    def __hash__(self):
        if not self._hash:
            self._hash = hash(tuple(self))
        return self._hash


class HashableDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._hash = None

    def __hash__(self):
        if not self._hash:
            self._hash = hash(tuple(sorted(self.items())))
        return self._hash


def make_hashable(json_object):
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
