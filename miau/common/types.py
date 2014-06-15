import sys
from numbers import Number

PY2 = sys.version_info < (3, 0)
PY3 = not PY2

if sys.version_info < (3, 0):
    StringTypes = (str, unicode)
    ustr = unicode
else:
    StringTypes = (str)
    ustr = str

def is_string(thing):
    return isinstance(thing, StringTypes)

# flask implementation of with_metaclass
# https://github.com/mitsuhiko/flask/blob/6ec83e18dca497a8fbfca6caca5999984bd32f2e/flask/_compat.py#L56-L73
def with_metaclass(meta, *bases):
    # This requires a bit of explanation: the basic idea is to make a
    # dummy metaclass for one level of class instantiation that replaces
    # itself with the actual metaclass. Because of internal type checks
    # we also need to make sure that we downgrade the custom metaclass
    # for one level to something closer to type (that's why __call__ and
    # __init__ comes back from type etc.).
    #
    # This has the advantage over six.with_metaclass in that it does not
    # introduce dummy classes into the final MRO.
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__
        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('temporary_class', None, {})
