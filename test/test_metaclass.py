# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest
from configvalidator import LoadException


class MyTestCase(unittest.TestCase):

    def test_something(self):
        from configvalidator.tools.basics import list_objects
        res = list_objects()
        self.assertListEqual(
            sorted(res["option_features"]), sorted(['sub_ini', 'default']))
        self.assertListEqual(
            sorted(res["section_features"]), sorted(['raw_section_input', 'default']))
        self.assertListEqual(
            sorted(res["validators"]),
            sorted(['error', 'or', 'default', 'json',
                    'email', 'url', 'ip', 'bool', 'float', 'str', 'generalizedTime', 'int', 'ipv6',
                    'regex', 'file', 'cert', 'and', 'ipv4', 'dir', 'path', 'port',
                    'items', 'item', 'netbios', "list", "dict", "base64",
                    'StripQuotationMark', 'strip_dir', 'strip_file', 'strip_path',
                    'empty', 'not-empty', 'one-off', "freePort"]))

    def test_load_validator(self):
        from configvalidator import load_validator
        with self.assertRaises(LoadException) as e:
            load_validator("NOT-DEFINED")
        self.assertEqual(str(e.exception), "no validator with the name NOT-DEFINED")

    def test_load_section_feature(self):
        from configvalidator.tools.basics import load_section_feature
        with self.assertRaises(LoadException) as e:
            load_section_feature("NOT-DEFINED")
        self.assertEqual(str(e.exception), "no Section feature with the name NOT-DEFINED")

    def test_load_option_feature(self):
        from configvalidator.tools.basics import load_option_feature
        with self.assertRaises(LoadException) as e:
            load_option_feature("NOT-DEFINED")
        self.assertEqual(str(e.exception), "no option feature with the name NOT-DEFINED")

    def test_add_new_class(self):
        from configvalidator.tools.basics import Validator
        from configvalidator import load_validator
        # try to loas class -> error
        with self.assertRaises(LoadException) as e:
            load_validator("DEMO_CLASS")
        self.assertEqual(str(e.exception), "no validator with the name DEMO_CLASS")
        # gen new class
        newclass = type("DEMO_CLASS", (Validator,), {"validate": lambda s, x: x})
        # load klass -> ok
        res = load_validator("DEMO_CLASS")
        self.assertEqual(newclass, res)
        # remove class so that other test pass
        from configvalidator.tools.basics import DATA_VALIDATOR
        del DATA_VALIDATOR["DEMO_CLASS"]
        with self.assertRaises(LoadException) as e:
            load_validator("DEMO_CLASS")
        self.assertEqual(str(e.exception), "no validator with the name DEMO_CLASS")
        
    def test_strip_validators(self):
        from configvalidator.validators import StripQuotationMarkPathValidator
        from configvalidator.validators import PathValidator
        self.assertEqual(PathValidator, StripQuotationMarkPathValidator()._validator.__class__)
        self.assertEqual("strip_path", StripQuotationMarkPathValidator.name)
        from configvalidator.validators import StripQuotationMarkFileValidator
        from configvalidator.validators import FileValidator
        self.assertEqual(FileValidator, StripQuotationMarkFileValidator()._validator.__class__)
        self.assertEqual("strip_file", StripQuotationMarkFileValidator.name)
        from configvalidator.validators import StripQuotationMarkDirValidator
        from configvalidator.validators import DirValidator
        self.assertEqual(DirValidator, StripQuotationMarkDirValidator()._validator.__class__)
        self.assertEqual("strip_dir", StripQuotationMarkDirValidator.name)


if __name__ == '__main__':
    unittest.main()
