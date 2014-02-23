"""Functions to force a certain data type or return TypeError, intended for
fast and safe JSON deserialization"""

from miau.common.types import StringTypes

def fstr(o):
    if isinstance(o, StringTypes):
        return o
    else:
        raise TypeError

def fint(o):
    if isinstance(o, int):
        return o
    else:
        raise TypeError
