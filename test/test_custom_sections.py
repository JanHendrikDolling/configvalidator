# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import testutils
from configvalidator import ConfigValidator
from configvalidator import AttributeDict
from configvalidator import ParserException


class MyTestCase(unittest.TestCase):

    def test_parsing_raw_section(self):
        input_dict = {
            "SectionB": {
                "option_B1": "Hallo",
                "option_B2": "Welt",
            },
        }
        config_dict = {
            "SectionB": {
                "__feature__": "raw_section_input",
            },
        }
        cp = testutils.get_cp(input_dict)
        res = cp.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionB, AttributeDict))
        self.assertEqual(2, len(res.SectionB))
        self.assertEqual("Hallo", res.SectionB.option_B1)
        self.assertEqual("Welt", res.SectionB.option_B2)

    def test_parsing_raw_section_partial(self):
        input_dict = {
            "SectionB": {
                "option_B1": "Hallo",
                "option_B2": "100",
                "option_B3": "90",
            },
        }
        config_dict = {
            "SectionB": {
                "__feature__": "raw_section_input",
                "validator": {
                    "type": "int",
                    "min": 95,
                },
                "raise_error": False,
            },
        }
        cp = testutils.get_cp(input_dict)
        res = cp.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.SectionB, AttributeDict))
        self.assertEqual(1, len(res.SectionB))
        self.assertEqual(100, res.SectionB.option_B2)

    def test_parsing_raw_section_min(self):
        input_dict = {
            "SectionB": {
                "option_B1": "Hallo",
                "option_B2": "Welt",
            },
        }
        config_dict = {
            "SectionB": {
                "__feature__": "raw_section_input",
                "min": 3,
            },
        }
        cp = testutils.get_cp(input_dict)
        with self.assertRaises(ParserException) as e:
            cp.parse(config_dict)
        self.assertEqual(
            str(e.exception),
            "error validating [SectionB]: minimum vailed options not reached")

    def test_parsing_raw_section_max(self):
        input_dict = {
            "SectionB": {
                "option_B1": "Hallo",
                "option_B2": "Welt",
            },
        }
        config_dict = {
            "SectionB": {
                "__feature__": "raw_section_input",
                "max": 1,
            },
        }
        cp = testutils.get_cp(input_dict)
        with self.assertRaises(ParserException) as e:
            cp.parse(config_dict)
        self.assertEqual(
            str(e.exception),
            "error validating [SectionB]: maximum vailed options reached")

    def test_parsing_raw_section_partial_with_min(self):
        input_dict = {
            "SectionB": {
                "option_B1": "Hallo",
                "option_B2": "100",
                "option_B3": "90",
            },
        }
        config_dict = {
            "SectionB": {
                "__feature__": "raw_section_input",
                "validator": {
                    "type": "int",
                    "min": 95,
                },
                "raise_error": False,
                "min": 2,
            },
        }
        cp = testutils.get_cp(input_dict)
        with self.assertRaises(ParserException) as e:
            cp.parse(config_dict)
        self.assertEqual(
            str(e.exception),
            "error validating [SectionB]: minimum vailed options not reached")

    def test_parsing_raw_section_partial_raise_error(self):
        input_dict = {
            "SectionB": {
                "option_B1": "Hallo",
                "option_B2": "100",
            },
        }
        config_dict = {
            "SectionB": {
                "__feature__": "raw_section_input",
                "validator": "int",
                "raise_error": True,
            },
        }
        cp = testutils.get_cp(input_dict)
        with self.assertRaises(ParserException) as e:
            cp.parse(config_dict)
        self.assertEqual(
            str(e.exception),
            "error validating [SectionB]: option_B1 - Input is no int")


if __name__ == '__main__':
    unittest.main()
