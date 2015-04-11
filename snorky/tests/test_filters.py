# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from snorky.services.datasync.dealers import filter_matches
import unittest


class TestFilters(unittest.TestCase):
    def test_eq(self):
        f = ['==', 'color', 'blue']
        self.assertTrue(filter_matches({'color': 'blue'}, f))
        self.assertFalse(filter_matches({'color': 'red'}, f))

        f = ['==', 'a', 1]
        self.assertTrue(filter_matches({'a': 1}, f))
        self.assertFalse(filter_matches({'a': 2}, f))
        # Use strong typing
        self.assertFalse(filter_matches({'a': '1'}, f))

    def test_lt(self):
        f = ['<', 'age', 21]
        self.assertTrue(filter_matches({'age': 20}, f))
        self.assertFalse(filter_matches({'age': 21}, f))
        self.assertFalse(filter_matches({'age': 22}, f))

        # Use strong typing
        self.assertFalse(filter_matches({'age': '20'}, f))

    def test_lte(self):
        f = ['<=', 'age', 21]
        self.assertTrue(filter_matches({'age': 20}, f))
        self.assertTrue(filter_matches({'age': 21}, f))
        self.assertFalse(filter_matches({'age': 22}, f))

        # Use strong typing
        self.assertFalse(filter_matches({'age': '20'}, f))

    def test_gt(self):
        f = ['>', 'age', 21]
        self.assertFalse(filter_matches({'age': 20}, f))
        self.assertFalse(filter_matches({'age': 21}, f))
        self.assertTrue(filter_matches({'age': 22}, f))

        # Use strong typing
        self.assertFalse(filter_matches({'age': '22'}, f))

    def test_gte(self):
        f = ['>=', 'age', 21]
        self.assertFalse(filter_matches({'age': 20}, f))
        self.assertTrue(filter_matches({'age': 21}, f))
        self.assertTrue(filter_matches({'age': 22}, f))

        # Use strong typing
        self.assertFalse(filter_matches({'age': '22'}, f))

    def test_not(self):
        f = ['not', ['==', 'color', 'blue']]
        self.assertFalse(filter_matches({'color': 'blue'}, f))
        self.assertTrue(filter_matches({'color': 'red'}, f))

        f = ['not', ['==', 'a', 1]]
        self.assertFalse(filter_matches({'a': 1}, f))
        self.assertTrue(filter_matches({'a': 2}, f))

    def test_and(self):
        f = ['and', ['>=', 'a', 3], ['<=', 'a', 7]]
        self.assertTrue(filter_matches({'a': 5}, f))
        self.assertFalse(filter_matches({'a': 2}, f))
        self.assertFalse(filter_matches({'a': 8}, f))

        f = ['and', ['==', 'a', 'foo'], ['==', 'b', 'bar']]
        self.assertTrue(filter_matches({'a': 'foo', 'b': 'bar'}, f))
        self.assertFalse(filter_matches({'a': 'foo', 'b': 'other'}, f))
        self.assertFalse(filter_matches({'a': 'other', 'b': 'bar'}, f))
        self.assertFalse(filter_matches({'a': 'other', 'b': 'other'}, f))
        self.assertFalse(filter_matches({'a': 'bar', 'b': 'foo'}, f))

    def test_or(self):
        f = ['or', ['<', 'a', 3], ['>', 'a', 7]]
        self.assertFalse(filter_matches({'a': 5}, f))
        self.assertTrue(filter_matches({'a': 2}, f))
        self.assertTrue(filter_matches({'a': 8}, f))

        f = ['or', ['==', 'a', 'foo'], ['==', 'b', 'bar']]
        self.assertTrue(filter_matches({'a': 'foo', 'b': 'bar'}, f))
        self.assertTrue(filter_matches({'a': 'foo', 'b': 'other'}, f))
        self.assertTrue(filter_matches({'a': 'other', 'b': 'bar'}, f))
        self.assertFalse(filter_matches({'a': 'other', 'b': 'other'}, f))
        self.assertFalse(filter_matches({'a': 'bar', 'b': 'foo'}, f))


if __name__ == "__main__":
    unittest.main()

