# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import testutils
from configvalidator import ConfigValidator, ParserException
from configvalidator.tools.basics import Validator
from configvalidator import AttributeDict
from configvalidator import remove_data, add_data


class MyTestCase(unittest.TestCase):

    @staticmethod
    def validate(inst, data):
        if "VAL" not in inst.data:
            raise Exception("need VAL")
        return inst.data["VAL"]

    @classmethod
    def setUpClass(cls):
        type("DEMO_CLASS", (Validator,), {"validate": MyTestCase.validate})

    def setUp(self):
        self.config_dict = {
            "SectionB": {
                "option_B2": {
                    "default": "INPUT",
                    "validator": "DEMO_CLASS",
                },
            },
        }
        from configvalidator.tools.basics import GLOBAL_DATA
        for key in list(GLOBAL_DATA.keys()):
            remove_data(key)

    @classmethod
    def tearDownClass(cls):
        from configvalidator.tools.basics import DATA_VALIDATOR
        del DATA_VALIDATOR["DEMO_CLASS"]

    def test_global(self):
        add_data("VAL", "foo")
        cp = testutils.get_cp()
        res = cp.parse(self.config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionB, AttributeDict))
        self.assertEqual(1, len(res.SectionB))
        self.assertEqual("foo", res.SectionB.option_B2)
        remove_data("VAL")
        with self.assertRaises(ParserException) as e:
            cp.parse(self.config_dict)
        self.assertEqual("error validating [SectionB]option_B2: need VAL", str(e.exception))

    def test_not_data(self):
        cp = testutils.get_cp()
        with self.assertRaises(ParserException) as e:
            cp.parse(self.config_dict)
        self.assertEqual("error validating [SectionB]option_B2: need VAL", str(e.exception))

    def test_local_data(self):
        cp = testutils.get_cp()
        cp.add_data("VAL", 123)
        res = cp.parse(self.config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionB, AttributeDict))
        self.assertEqual(1, len(res.SectionB))
        self.assertEqual(123, res.SectionB.option_B2)
        cp.remove_data("VAL")
        with self.assertRaises(ParserException) as e:
            cp.parse(self.config_dict)
        self.assertEqual("error validating [SectionB]option_B2: need VAL", str(e.exception))


if __name__ == '__main__':
    unittest.main()
