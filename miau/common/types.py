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
