# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
from snorky.services.base import RPCService, rpc_command
from snorky.hashable import make_hashable

from snorky.tests.utils.rpc import RPCTestMixin
from unittest import TestCase
import unittest

class TestHashable(unittest.TestCase):
    def test_object(self):
        hash(make_hashable({
            "name": "Alice",
            "points": 200
        }))

    def test_array(self):
        hash(make_hashable([1, "foo"]))

    def test_trivial(self):
        self.assertEqual(hash(make_hashable("string")), hash("string"))
        self.assertEqual(hash(make_hashable(23)), hash(23))
        self.assertEqual(hash(make_hashable(None)), hash(None))

    def test_complex(self):
        hash(make_hashable({
            "a": {
                "list": [
                    "foo",
                    21,
                    None,
                    { "b": 3.14 }
                ],
                "empty_dict": {},
                "empty_list": [],
            }
        }))

    def assert_equal_hashable(self, json_object):
        self.assertEqual(json_object, make_hashable(json_object))

    def test_equal_scalar(self):
        self.assert_equal_hashable("meow")

    def test_equal_dict(self):
        self.assert_equal_hashable({"foo": "bar"})

    def test_equal_list(self):
        self.assert_equal_hashable([1, 2])

    def assert_equal_hashable_json(self, json_object):
        # Check the object if the same if it's encoded in JSON after being
        # made hashable
        hashable_json_object = make_hashable(json_object)
        decoded_json_object = json.loads(json.dumps(hashable_json_object))
        self.assertEqual(hashable_json_object, decoded_json_object)

    def test_json_scalar(self):
        self.assert_equal_hashable_json("hi")

    def test_json_list(self):
        self.assert_equal_hashable_json([1, 2])

    def test_json_dict(self):
        self.assert_equal_hashable_json({ "foo": "bar" })


class DictService(RPCService):
    def __init__(self, name):
        RPCService.__init__(self, name)
        self.my_dict = {}

    @rpc_command
    def put(self, req, key, value):
        self.my_dict[key] = value

    @rpc_command
    def get(self, req, key):
        return self.my_dict[key]


class TestComplexHashableInRPC(RPCTestMixin, TestCase):
    def setUp(self):
        self.service = DictService("dict")

    def base_test_service(self, key):
        response = self.rpcCall(self.service, None,
                                "put", key=key, value="value")
        self.assertEqual(response, None)

        response = self.rpcCall(self.service, None,
                                "get", key=key)
        self.assertEqual(response, "value")

    def test_simple_values(self):
        self.base_test_service("key")

    def test_list(self):
        self.base_test_service(["a", "b"])

    def test_dict(self):
        self.base_test_service({ "name": "Alice", "color": "blue" })


if __name__ == "__main__":
    unittest.main()
