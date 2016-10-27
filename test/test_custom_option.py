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
from configvalidator import ConfigValidator
from configvalidator import AttributeDict
from configvalidator import ParserException
from configvalidator.tools.basics import Validator


class MyTestCase(unittest.TestCase):

    def test_parsing_sub_ini_invalid_path(self):
        config_dict = {
            "SectionB": {
                "option_B2": {
                    "feature": "sub_ini",
                    "default": os.path.join(
                        testutils.get_test_utils_base(),
                        "data",
                        "not_exist",
                        "foo.ini"),
                    "config": {},
                },
            },
        }
        cv = testutils.get_cp()
        with self.assertRaises(ParserException) as e:
            cv.parse(config_dict)
        self.assertEqual(
            str(e.exception),
            "error validating [SectionB]option_B2: path \"{testutils}\" doesn't exist".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "not_exist", "foo.ini")))

    def test_parsing_sub_ini(self):
        sub_ini_config = dict(A=dict(b={}))
        config_dict = {
            "Section": {
                "option": {
                    "feature": "sub_ini",
                    "config": sub_ini_config,
                },
            },
        }
        cp = testutils.CPStub2(
            dict(Section=dict(option=os.path.join(testutils.get_test_utils_base(), "data", "exist", "default.ini"))))
        cv = ConfigValidator(cp=cp)
        res = cv.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.Section, AttributeDict))
        self.assertEqual(1, len(res.Section))
        self.assertTrue(isinstance(res.Section.option, AttributeDict))
        self.assertEqual(1, len(res.Section.option))
        self.assertTrue(isinstance(res.Section.option.A, AttributeDict))
        self.assertEqual(1, len(res.Section.option.A))
        self.assertEqual('Hallo Welt', res.Section.option.A.b)

    def test_parsing_sub_ini_args(self):
        # the 'config_dict' for the ConfigValidator there the date is in the
        # cp_init_args['data_dict']
        sub_ini_config = {
            "SectionB": {
                "__test__": "default",
                "option_B2": {
                    "validator": "int",
                },
            },
        }
        # parameters for the new cp instance (here this is the CPStub3 ->
        # so the parameter 'data_dict' set the new values)
        cp_init_args = {
            "data_dict": {
                "SectionB": {
                    "option_B2": "50"
                },
            }
        }
        config_dict = {
            "foo": {
                "bar": {
                    "feature": "sub_ini",
                    "config": sub_ini_config,
                    "feature_key": "__test__",
                },
            },
        }
        # value '...empty.ini' will be ignored because the CPStub3 get the "cp_init_args" parametes
        # this parameters sets the new values for the config parser stub
        cp = testutils.CPStub3(
            dict(foo=dict(bar=os.path.join(testutils.get_test_utils_base(), "data", "exist", "empty.ini"))))
        cv = ConfigValidator(cp=cp, cp_init_args=cp_init_args)
        res = cv.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.foo, AttributeDict))
        self.assertEqual(1, len(res.foo))
        self.assertTrue(isinstance(res.foo.bar, AttributeDict))
        self.assertEqual(1, len(res.foo.bar))
        self.assertTrue(isinstance(res.foo.bar.SectionB, AttributeDict))
        self.assertEqual(1, len(res.foo.bar.SectionB))
        self.assertEqual(50, res.foo.bar.SectionB.option_B2)

    def test_parsing_sub_ini_with_data(self):
        from configvalidator import remove_data, add_data
        from configvalidator.tools.basics import GLOBAL_DATA
        for key in list(GLOBAL_DATA.keys()):
            remove_data(key)
        type("DEMO_CLASS_123", (Validator,), {"validate": MyTestCase.validate})
        sub_ini_config = {
            "SectionB": {
                "option_B2": {
                    "default": "IN...",
                    "validator": "DEMO_CLASS_123",
                },
            },
        }
        config_dict = {
            "foo": {
                "bar": {
                    "feature": "sub_ini",
                    "config": sub_ini_config,
                },
            },
        }
        cp = testutils.CPStub3(dict(foo=dict(bar=os.path.join(testutils.get_test_utils_base(), "data", "exist", "empty.ini"))))
        cv = ConfigValidator(cp=cp)
        # res = cv.parse(config_dict)
        with self.assertRaises(ParserException) as e:
            cv.parse(config_dict)
        self.assertEqual("error validating [foo]bar: error validating [SectionB]option_B2: need VAL1", str(e.exception))
        cv.add_data("VAL1", "foo")
        res = cv.parse(config_dict)
        self.assertTrue(isinstance(res, AttributeDict))
        self.assertEqual(1, len(res))
        self.assertTrue(isinstance(res.foo, AttributeDict))
        self.assertEqual(1, len(res.foo))
        self.assertTrue(isinstance(res.foo.bar, AttributeDict))
        self.assertEqual(1, len(res.foo.bar))
        self.assertTrue(isinstance(res.foo.bar.SectionB, AttributeDict))
        self.assertEqual(1, len(res.foo.bar.SectionB))
        self.assertEqual("foo", res.foo.bar.SectionB.option_B2)
        add_data("VAL2", "bar")
        res2 = cv.parse(config_dict)
        self.assertTrue(isinstance(res2, AttributeDict))
        self.assertEqual(1, len(res2))
        self.assertTrue(isinstance(res2.foo, AttributeDict))
        self.assertEqual(1, len(res2.foo))
        self.assertTrue(isinstance(res2.foo.bar, AttributeDict))
        self.assertEqual(1, len(res2.foo.bar))
        self.assertTrue(isinstance(res2.foo.bar.SectionB, AttributeDict))
        self.assertEqual(1, len(res2.foo.bar.SectionB))
        self.assertEqual("bar", res2.foo.bar.SectionB.option_B2)
        remove_data("VAL2")
        self.assertEqual(0, len(GLOBAL_DATA.keys()))
        from configvalidator.tools.basics import DATA_VALIDATOR
        del DATA_VALIDATOR["DEMO_CLASS_123"]

    @staticmethod
    def validate(inst, data):
        if "VAL1" not in inst.data:
            raise Exception("need VAL1")
        if "VAL2" in inst.data:
            return inst.data["VAL2"]
        return inst.data["VAL1"]

if __name__ == '__main__':
    unittest.main()
