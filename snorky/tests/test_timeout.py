# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from unittest import TestCase
from mock import Mock
from snorky.tests.utils.timeout import TestTimeoutFactory
import unittest


class TestTimeouts(TestCase):
    def setUp(self):
        self.time_man = TestTimeoutFactory()
        self.mock = Mock()

    def test_add_and_run(self):
        self.time_man.call_later(5, self.mock, "foo", bar=5)
        self.assertEqual(self.time_man.timeouts_pending, 1)

        self.time_man.process_all()
        self.mock.assert_called_once_with("foo", bar=5)

    def test_cancel(self):
        timeout = self.time_man.call_later(5, self.mock, "foo", bar=5)
        self.assertEqual(self.time_man.timeouts_pending, 1)

        timeout.cancel()
        self.assertEqual(self.time_man.timeouts_pending, 0)

        self.time_man.process_all()
        self.assertFalse(self.mock.called)


if __name__ == "__main__":
    unittest.main()
