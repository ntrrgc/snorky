import sys

if sys.version_info < (3, 0):
    StringTypes = (str, unicode)
    ustr = unicode
else:
    StringTypes = (str)
    ustr = str
