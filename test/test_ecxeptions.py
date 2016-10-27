# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest
from configvalidator import ValidatorException


class MyTestCase(unittest.TestCase):

    def test_from_list(self):
        l = ["Hello", "world"]
        e = ValidatorException.from_list(l)
        self.assertEqual(type(e), ValidatorException)
        self.assertListEqual(e.info, ["Hello", "world"])
        self.assertListEqual(e.errors, [("Hello", None), ("world", None)])
        # complex
        ex = Exception("world")
        lx = [("Hello", ex), "demo"]
        e2 = ValidatorException.from_list(lx)
        self.assertEqual(type(e2), ValidatorException)
        self.assertListEqual(e2.info, ["Hello", "demo"])
        self.assertListEqual(e2.errors, [("Hello", ex), ("demo", None)])


if __name__ == '__main__':
    unittest.main()
