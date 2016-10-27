# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import testutils
from configvalidator import ConfigValidator
from configvalidator import ParserException, InitException


class MyTestCase(unittest.TestCase):

    def test_init(self):
        with self.assertRaises(InitException) as e:
            ConfigValidator(testutils.CPStub())
        self.assertEqual(
            str(e.exception),
            "No such method \"read\". Need to implement the ConfigParser interface")

    def test_parsing_empty_required_input(self):
        config_dict = {
            "SectionB": {
                "option_B2": {},
            },
        }
        cp = testutils.get_cp()
        with self.assertRaises(ParserException) as e:
            cp.parse(config_dict)
        self.assertEqual(
            str(e.exception),
            "No value for Section/Option: 'SectionB'/'option_B2'")

    def test_parsing_validator_parameter_error(self):
        config_dict = {
            "SectionB": {
                "option_B2": {
                    "validator": {
                        "type": "default",
                        "arg1": "error",
                    },
                    "default": "10",
                },
            },
        }
        cp = testutils.get_cp()
        with self.assertRaises(ParserException) as e:
            res = cp.parse(config_dict)
        self.assertTrue(str(e.exception).startswith("error validating [SectionB]option_B2: error init validator 'default' |"))

    def test_parsing_dependencies_circle(self):
        config_dict = testutils.get_dict()
        config_dict["SectionA"] = testutils.get_dict()
        config_dict["SectionA"]["option_A1"] = dict(
            default="10",
            validator=dict(
                type="int",
                min=("SectionA", "option_A2")),
            depends=["min"])
        config_dict["SectionA"]["option_A2"] = dict(
            default="10",
            validator=dict(
                type="int",
                min=("SectionA", "option_A1")),
            depends=["min"])
        cp = testutils.get_cp()
        with self.assertRaises(ParserException) as e:
            cp.parse(config_dict)
        error_msg, dep_msg = str(e.exception).split("\n")
        error_msg_1 = "error validating [SectionA]option_A1: circle reference with [SectionA]option_A2"
        error_msg_2 = "error validating [SectionA]option_A2: circle reference with [SectionA]option_A1"
        dep_msg_1 = "not all dependencies resolved: 'SectionA'/'option_A2'|'SectionA'/'option_A1'"
        dep_msg_2 = "not all dependencies resolved: 'SectionA'/'option_A1'|'SectionA'/'option_A2'"
        try:
            self.assertEqual(error_msg, error_msg_1)
        except:
            self.assertEqual(error_msg, error_msg_2)
        try:
            self.assertEqual(dep_msg_1, dep_msg)
        except:
            self.assertEqual(dep_msg_2, dep_msg)

    def test_parsing_dependencies_missing(self):
        config_dict = testutils.get_dict()
        config_dict["SectionA"] = testutils.get_dict()
        config_dict["SectionA"]["option_A1"] = dict(
            default="10",
            validator=dict(
                type="int",
                min=("SectionA", "option_A2")),
            depends=["min"])
        cp = testutils.get_cp()
        with self.assertRaises(ParserException) as e:
            cp.parse(config_dict)
        self.assertEqual(
            str(e.exception),
            "not all dependencies resolved: 'SectionA'/'option_A1'")

    def test_parsing_dependencies_syntax(self):
        config_dict = testutils.get_dict()
        config_dict["SectionA"] = testutils.get_dict()
        config_dict["SectionA"]["option_A1"] = dict(
            default="10",
            validator=dict(
                type="int", min=(10, "SectionA")),
            depends=["min"])
        cp = testutils.get_cp()
        with self.assertRaises(ParserException) as e:
            cp.parse(config_dict)
        self.assertEqual(str(e.exception), "error validating [SectionA]option_A1: depends syntax: 'str: (str, str)'")

    def test_error_feature(self):
        from configvalidator.tools.basics import SectionFeature

        def _(self, parse_obj, section_dict):
            raise Exception("fail")
        type("Raise_error", (SectionFeature,), {"parse_section": _})
        config_dict = {
            "SectionB": {
                "__feature__": "Raise_error",
            },
        }
        cp = testutils.get_cp()
        with self.assertRaises(ParserException) as e:
            cp.parse(config_dict)
        self.assertEqual("Error parsing section SectionB: fail", str(e.exception))
        from configvalidator.tools.basics import DATA_SECTION_FEATURE
        del DATA_SECTION_FEATURE["Raise_error"]

if __name__ == '__main__':
    unittest.main()
