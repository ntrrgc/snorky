# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from snorky.types import MultiDict
from unittest import TestCase
import unittest


class TestMultiDict(TestCase):
    def test_add(self):
        self.multidict = MultiDict()
        self.multidict.add("key", "val1")
        self.assertEqual(self.multidict["key"], {"val1"})
        self.multidict.add("key", "val2")
        self.assertEqual(self.multidict["key"], {"val1", "val2"})

    def test_remove(self):
        self.test_add()
        self.multidict.remove("key", "val1")
        self.assertEqual(self.multidict["key"], {"val2"})
        self.multidict.remove("key", "val2")
        self.assertTrue("key" not in self.multidict)

    def test_get_set(self):
        self.test_add()
        self.multidict.remove("key", "val1")
        self.assertEqual(self.multidict.get_set("key"), {"val2"})
        self.multidict.remove("key", "val2")
        self.assertEqual(self.multidict.get_set("key"), set())

    def test_in_set(self):
        self.test_add()
        self.assertTrue(self.multidict.in_set("key", "val1"))
        self.assertTrue(self.multidict.in_set("key", "val2"))
        self.multidict.remove("key", "val1")
        self.multidict.remove("key", "val2")
        self.assertFalse(self.multidict.in_set("key", "val1"))
        self.assertFalse(self.multidict.in_set("key", "val2"))



if __name__ == "__main__":
    unittest.main()
