# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""
try:
    import configvalidator
except ImportError:
    import sys
    import os
    sys.path.append(os.getcwd())
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import testutils
from configvalidator import ConfigValidator
from configvalidator import AttributeDict
from configvalidator import ParserException


class MyTestCase(unittest.TestCase):

    def test_parsing_empty_all(self):
        cp = testutils.get_cp()
        res = cp.parse({})
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(0, len(res))

    def test_parsing_input_required_input(self):
        input_dict = {
            "SectionB": {
                "option_B2": "Hallo",
            },
        }
        config_dict = {
            "SectionB": {
                "option_B2": {},
            },
        }
        cp = testutils.get_cp(input_dict)
        res = cp.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionB, AttributeDict))
        self.assertEqual(1, len(res.SectionB))
        self.assertEqual("Hallo", res.SectionB.option_B2)

    def test_parsing_empty_default_input(self):
        config_dict = {
            "SectionB": {
                "option_B2": {
                    "default": "10",
                },
            },
        }
        cp = testutils.get_cp()
        res = cp.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionB, AttributeDict))
        self.assertEqual(1, len(res.SectionB))
        self.assertEqual("10", res.SectionB.option_B2)

    def test_parsing_section_feature(self):
        config_dict = {
            "SectionB": {
                "__feature__": "default",
                "option_B2": {
                    "default": "10",
                },
            },
        }
        cp = testutils.get_cp()
        res = cp.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionB, AttributeDict))
        self.assertEqual(1, len(res.SectionB))
        self.assertEqual("10", res.SectionB.option_B2)

    def test_parsing_section_feature_alternative_key_name(self):
        config_dict = {
            "SectionB": {
                "__test__": "default",
                "option_B2": {
                    "default": "10",
                },
            },
        }
        cp = testutils.get_cp()
        res = cp.parse(config_dict, feature_key="__test__")
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionB, AttributeDict))
        self.assertEqual(1, len(res.SectionB))
        self.assertEqual("10", res.SectionB.option_B2)

    def test_parsing_option_feature(self):
        config_dict = {
            "SectionB": {
                "option_B2": {
                    "__feature__": "default",
                    "default": "10",
                },
            },
        }
        cp = testutils.get_cp()
        res = cp.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionB, AttributeDict))
        self.assertEqual(1, len(res.SectionB))
        self.assertEqual("10", res.SectionB.option_B2)

    def test_parsing_validator(self):
        config_dict = {
            "SectionB": {
                "option_B2": {
                    "validator": "default",
                    "default": "10",
                },
            },
        }
        cp = testutils.get_cp()
        res = cp.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionB, AttributeDict))
        self.assertEqual(1, len(res.SectionB))
        self.assertEqual("10", res.SectionB.option_B2)

    def test_parsing_validator_parameter(self):
        config_dict = {
            "SectionB": {
                "option_B2": {
                    "validator": {
                        "type": "default",
                    },
                    "default": "10",
                },
            },
        }
        cp = testutils.get_cp()
        res = cp.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionB, AttributeDict))
        self.assertEqual(1, len(res.SectionB))
        self.assertEqual("10", res.SectionB.option_B2)

    def test_parsing_dependencies(self):
        input_dict = {
            "SectionA": {
                "option_A2": "5",
            },
        }
        config_dict = {
            "SectionA": {
                "option_A1": {
                    "default": "10",
                    "validator": "int",
                },
                "option_A2": {
                    "validator": {
                        "type": "int",
                        "min": 0,
                        "max": ("SectionA", "option_A1"),
                    },
                    "depends": ["max"],
                },
            },
        }
        cp = testutils.get_cp(input_dict)
        res = cp.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionA, AttributeDict))
        self.assertEqual(2, len(res.SectionA))
        self.assertEqual(10, res.SectionA.option_A1)
        self.assertEqual(5, res.SectionA.option_A2)

    def test_easy_input(self):
        input_dict = {
            "SectionA": {
                "option_A1": "5",
            },
        }
        config_dict = {
            "SectionA": {
                "option_A1": "int",
            },
        }
        cp = testutils.get_cp(input_dict)
        res = cp.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionA, AttributeDict))
        self.assertEqual(1, len(res.SectionA))
        self.assertEqual(5, res.SectionA.option_A1)


if __name__ == '__main__':
    unittest.main()
