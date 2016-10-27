# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest
from configvalidator.tools.result import AttributeDict


class MyTestCase(unittest.TestCase):

    def test_result(self):
        res = AttributeDict(dict(a="hello", b="world"))
        self.assertEqual("hello", res.a)
        self.assertEqual("hello", res["a"])
        self.assertEqual("world", res.b)
        self.assertEqual("world", res["b"])

    def test_error(self):
        res = AttributeDict()
        with self.assertRaises(KeyError) as e:
            res.value

    def test_section_option(self):
        res = AttributeDict(section=dict(option="1"), get="test")
        self.assertEqual("1", res.get("section", "option"))
        self.assertEqual("test", res["get"])

    def test_section_option_error(self):
        res = AttributeDict(section=dict())
        with self.assertRaises(KeyError) as e:
            res.get("section", "option")


if __name__ == '__main__':
    unittest.main()
