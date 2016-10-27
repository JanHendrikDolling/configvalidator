# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""
import os
import sys
try:
    import mock
except ImportError:
    from unittest import mock
import re
import types
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from configvalidator import ValidatorException
from configvalidator import ParserException, InitException
import testutils


class Test(unittest.TestCase):

    def test_default(self):
        from configvalidator.validators import DefaultValidator
        default = DefaultValidator()
        default.validate("")
        with self.assertRaises(ValidatorException) as e1:
            default.validate(10)
        self.assertEqual(str(e1.exception), "input must be a string.")

    def test_String(self):
        from configvalidator.validators import StringValidator
        no_limits = StringValidator()
        no_limits.validate("")
        no_limits.validate("Hallo Welt")
        min_length = StringValidator(min_length=5)
        with self.assertRaises(ValidatorException) as e1:
            min_length.validate("")
        self.assertEqual(str(e1.exception), "minimum string length: 5")
        with self.assertRaises(ValidatorException) as e2:
            min_length.validate("1234")
        self.assertEqual(str(e2.exception), "minimum string length: 5")
        min_length.validate("12345")
        max_length = StringValidator(max_length=6)
        max_length.validate("Hallo")
        with self.assertRaises(ValidatorException) as e3:
            max_length.validate("Hallo Welt")
        self.assertEqual(str(e3.exception), "maximum string length: 6")

    def test_error(self):
        from configvalidator.validators import ErrorValidator
        er = ErrorValidator(error_msg="the error")
        with self.assertRaises(ValidatorException) as e:
            er.validate("....")
        self.assertEqual(str(e.exception), "the error")

    def test_emtpy(self):
        from configvalidator.validators import EmptyValidator
        val = EmptyValidator()
        self.assertEqual("", val.validate(""))
        with self.assertRaises(ValidatorException) as e:
            val.validate("....")
        self.assertEqual(str(e.exception), "The input is not Empty.")

    def test_non_empty(self):
        from configvalidator.validators import NotEmptyValidator
        val = NotEmptyValidator()
        self.assertEqual("asdfghjkl", val.validate("asdfghjkl"))
        with self.assertRaises(ValidatorException) as e:
            val.validate("")
        self.assertEqual(str(e.exception), "The input is Empty.")

    def test_bool(self):
        from configvalidator.validators import BoolValidator
        bv = BoolValidator()
        bv.validate("yes")
        bv.validate("y")
        bv.validate("true")
        bv.validate("t")
        bv.validate("1")
        bv.validate("no")
        bv.validate("n")
        bv.validate("false")
        bv.validate("f")
        bv.validate("0")
        with self.assertRaises(ValidatorException) as e1:
            bv.validate("")
        self.assertEqual(
            str(e1.exception),
            "allowed values: yes, no, y, n, true, false, t, f, 1, 0")
        with self.assertRaises(ValidatorException) as e2:
            bv.validate("test")
        self.assertEqual(
            str(e2.exception),
            "allowed values: yes, no, y, n, true, false, t, f, 1, 0")

    def test_int(self):
        from configvalidator.validators import IntValidator
        no_limits = IntValidator()
        no_limits.validate("0")
        no_limits.validate("-10")
        no_limits.validate("1000")
        with self.assertRaises(ValidatorException) as e1:
            no_limits.validate("test")
        self.assertEqual(
            str(e1.exception),
            "Input is no int")
        min = IntValidator(min=1000)
        min.validate("1000")
        with self.assertRaises(ValidatorException) as e2:
            min.validate("10")
        self.assertEqual(str(e2.exception), "minimum: 1000")
        max = IntValidator(max=50)
        max.validate("-5000")
        with self.assertRaises(ValidatorException) as e3:
            max.validate("51")
        self.assertEqual(str(e3.exception), "maximum: 50")

    def test_min_max_init_error(self):
        from configvalidator.validators import IntValidator
        with self.assertRaises(InitException) as e1:
            IntValidator(min="test")
        self.assertEqual(str(e1.exception), "min must be a number")
        with self.assertRaises(InitException) as e2:
            IntValidator(max="test")
        self.assertEqual(str(e2.exception), "max must be a number")
        from configvalidator.validators import FloatValidator
        with self.assertRaises(InitException) as e3:
            FloatValidator(min="test")
        self.assertEqual(str(e3.exception), "min must be a number")
        with self.assertRaises(InitException) as e4:
            FloatValidator(max="test")
        self.assertEqual(str(e4.exception), "max must be a number")
        from configvalidator.validators import StringValidator
        with self.assertRaises(InitException) as e5:
            StringValidator(min_length="test")
        self.assertEqual(str(e5.exception), "min_length must be a number")
        with self.assertRaises(InitException) as e6:
            StringValidator(max_length="test")
        self.assertEqual(str(e6.exception), "max_length must be a number")

    def test_float(self):
        from configvalidator.validators import FloatValidator
        no_limits = FloatValidator()
        no_limits.validate("10.50")
        with self.assertRaises(ValidatorException) as e1:
            no_limits.validate("test")
        self.assertEqual(str(e1.exception), "Input is no float")
        min = FloatValidator(min=10.50)
        min.validate("100.2")
        with self.assertRaises(ValidatorException) as e2:
            min.validate("10")
        self.assertEqual(str(e2.exception), "minimum: 10.5")
        max = FloatValidator(max=50)
        max.validate("-5000")
        with self.assertRaises(ValidatorException) as e3:
            max.validate("50.1")
        self.assertEqual(str(e3.exception), "maximum: 50.0")

    def test_json(self):
        from configvalidator.validators import JsonValidator
        v = JsonValidator()
        v.validate("{}")
        with self.assertRaises(ValidatorException) as e:
            v.validate("foo")
        self.assertEqual(str(e.exception), "Invalid json input")

    def test_path(self):
        from configvalidator.validators import PathValidator
        no_limits = PathValidator()
        no_limits.validate(
            os.path.join(testutils.get_test_utils_base(), "data", "exist"))
        with self.assertRaises(ValidatorException) as e1:
            no_limits.validate(
                os.path.join(testutils.get_test_utils_base(), "data", "not_exist"))
        self.assertEqual(str(e1.exception), "path \"{testutils}\" doesn't exist".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "not_exist")))
        absolute = PathValidator(absolute=True)
        absolute.validate(os.path.dirname(__file__))
        with self.assertRaises(ValidatorException) as e2:
            absolute.validate(os.path.join(testutils.get_test_utils_base(), "data", "exist"))
        self.assertEqual("path \"{testutils}\" is relative but must be absolute".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "exist")), str(e2.exception))
        allowed_prefix = PathValidator(allowed_prefix=[
            os.path.join(
                testutils.get_test_utils_base(),
                "data",
                "exist",
                "a"),
            os.path.join(testutils.get_test_utils_base(), "data", "exist", "b")
        ])
        allowed_prefix.validate(
            os.path.join(testutils.get_test_utils_base(), "data", "exist", "a")
        )
        with self.assertRaises(ValidatorException) as e3:
            allowed_prefix.validate(
                os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "a",
                    "not_exist"))
        self.assertEqual(str(e3.exception), "path \"{testutils}\" doesn't exist".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "exist", "a", "not_exist")))
        with self.assertRaises(ValidatorException) as e4:
            allowed_prefix.validate(
                os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "c"))
        self.assertEqual(
            str(e4.exception),
            "path \"{testutils}\" is not in allowed prefixes".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "exist", "c")))
        disallowed_prefix = PathValidator(
            disallowed_prefix=[os.path.join(testutils.get_test_utils_base(), "data", "exist", "a")])
        disallowed_prefix.validate(
            os.path.join(testutils.get_test_utils_base(), "data", "exist", "b"))
        with self.assertRaises(ValidatorException) as e5:
            disallowed_prefix.validate(
                os.path.join(testutils.get_test_utils_base(), "data", "exist", "a"))
        self.assertEqual(
            str(e5.exception),
            "prefix: ({path}) not allowed".format(path=os.path.join(testutils.get_test_utils_base(), "data", "exist", "a")))
        with self.assertRaises(ValidatorException) as e6:
            disallowed_prefix.validate(
                os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "c",
                    "not_exist")
            )
        self.assertEqual(str(e6.exception), "path \"{testutils}\" doesn't exist".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "exist", "c", "not_exist")))

    def test_path_init(self):
        from configvalidator.validators import PathValidator
        with self.assertRaises(InitException) as e:
            PathValidator(allowed_prefix={})
        self.assertEqual("invalid allowed_prefix input", str(e.exception))
        with self.assertRaises(InitException) as e:
            PathValidator(disallowed_prefix={})
        self.assertEqual("invalid disallowed_prefix input", str(e.exception))
        p1 = PathValidator(allowed_prefix="test")
        self.assertListEqual(["test"], p1._allowed_prefix)
        p2 = PathValidator(disallowed_prefix="test")
        self.assertListEqual(["test"], p2._disallowed_prefix)

    def test_path_raise(self):
        from configvalidator.validators import PathValidator
        p = PathValidator(absolute=True)
        with self.assertRaises(ValidatorException) as e:
            p.validate(os.path.join(testutils.get_test_utils_base(), "data", "exist", "b"))
        self.assertEqual("path \"{testutils}\" is relative but must be absolute".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "exist", "b")), str(e.exception))
        p2 = PathValidator(absolute=False)
        with self.assertRaises(ValidatorException) as e2:
            p2.validate(os.path.abspath(os.path.join(testutils.get_test_utils_base(), "data", "exist", "b")))
        self.assertEqual("path \"{testutils}\" is absolute but must be relative".format(testutils=os.path.abspath(os.path.join(testutils.get_test_utils_base(), "data", "exist", "b"))), str(e2.exception))
        p3 = PathValidator()
        with mock.patch('os.path.exists') as m:
            m.side_effect = Exception('foo')
            with self.assertRaises(ValidatorException) as e:
                p3.validate("test")
            self.assertEqual("Error: foo", str(e.exception))

    def test_file(self):
        from configvalidator.validators import FileValidator
        no_limits = FileValidator()
        no_limits.validate(
            os.path.join(
                testutils.get_test_utils_base(),
                "data",
                "exist",
                "empty.ini"))
        with self.assertRaises(ValidatorException) as e1:
            no_limits.validate(
                os.path.join(testutils.get_test_utils_base(), "data", "exist"))
        self.assertEqual(str(e1.exception), "path \"{testutils}\" is not an file".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "exist")))
        with self.assertRaises(ValidatorException) as e2:
            no_limits.validate(
                os.path.join(testutils.get_test_utils_base(), "data", "not_exist"))
        self.assertEqual(str(e2.exception), "path \"{testutils}\" doesn't exist".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "not_exist")))

    def test_dir(self):
        from configvalidator.validators import DirValidator
        no_limits = DirValidator()
        no_limits.validate(
            os.path.join(testutils.get_test_utils_base(), "data", "exist"))
        with self.assertRaises(ValidatorException) as e1:
            no_limits.validate(
                os.path.join(testutils.get_test_utils_base(), "data", "not_exist".format(testutils=testutils.get_test_utils_base())))
        self.assertEqual(str(e1.exception), "path \"{testutils}\" doesn't exist".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "not_exist")))
        with self.assertRaises(ValidatorException) as e2:
            no_limits.validate(
                os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "empty.ini"))
        self.assertEqual(str(e2.exception), "path \"{testutils}\" is not an directory.".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "exist", "empty.ini")))
        dir_structure = DirValidator(
            include_dirs=["log"],
            include_files=["version.json"],
            exclude_dirs=["not_allowed_dir"],
            exclude_files=["not_allowed.file"],
        )
        dir_structure.validate(
            os.path.join(
                testutils.get_test_utils_base(),
                "data",
                "exist",
                "structure",
                "1"))
        with self.assertRaises(ValidatorException) as e3:
            dir_structure.validate(
                os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "structure",
                    "2"))
        self.assertEqual(
            str(e3.exception),
            "path \"{path}\" exist".format(path=os.path.join(testutils.get_test_utils_base(), "data", "exist", "structure", "2", "not_allowed.file")))
        with self.assertRaises(ValidatorException) as e4:
            dir_structure.validate(
                os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "structure",
                    "3"))
        self.assertEqual(
            str(e4.exception),
            "path \"{path}\" exist".format(path=os.path.join(testutils.get_test_utils_base(), "data", "exist", "structure", "3", "not_allowed_dir")))
        with self.assertRaises(ValidatorException) as e5:
            dir_structure.validate(
                os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "structure",
                    "4"))
        self.assertEqual(
            str(e5.exception),
            "path dosen't \"{path}\" exist".format(path=os.path.join(testutils.get_test_utils_base(), "data", "exist", "structure", "4", "version.json")))

    def test_port(self):
        from configvalidator.validators import PortValidator
        v = PortValidator()
        v.validate("65535")
        v.validate("89")
        v.validate("0")
        with self.assertRaises(ValidatorException) as e1:
            v.validate("-1")
        self.assertEqual(str(e1.exception), "port range [0-65535]")
        with self.assertRaises(ValidatorException) as e2:
            v.validate("65536")
        self.assertEqual(str(e2.exception), "port range [0-65535]")
        non_zero = PortValidator(allow_null=False)
        with self.assertRaises(ValidatorException) as e3:
            non_zero.validate("0")
        self.assertEqual(str(e3.exception), "port range [1-65535]")
        non_zero.validate("1")
        non_zero.validate("65535")
        with self.assertRaises(ValidatorException) as e4:
            non_zero.validate("65536")
        self.assertEqual(str(e4.exception), "port range [1-65535]")

    def test_regex(self):
        from configvalidator.validators import RegexValidator
        normal = RegexValidator(pattern="[^@]")
        normal.validate("test")
        with self.assertRaises(ValidatorException) as e1:
            normal.validate("@test")
        self.assertEqual(str(e1.exception), "No Matching")
        flags = RegexValidator(pattern="[A-Z]", flags=re.IGNORECASE)
        flags.validate("A")
        flags.validate("a")
        with self.assertRaises(ValidatorException) as e2:
            flags.validate("9")
        self.assertEqual(str(e2.exception), "No Matching")

    def test_regex_mock(self):
        from configvalidator.validators import RegexValidator
        with mock.patch('re.compile') as m:
            m.side_effect = Exception('foo')
            with self.assertRaises(InitException) as e1:
                RegexValidator(pattern="")
            self.assertEqual("error init regex: foo", str(e1.exception))
        p1 = RegexValidator(pattern="")
        p1._pattern = mock.Mock(**{"match.side_effect": Exception('Boom!')})
        with self.assertRaises(ValidatorException) as e2:
            p1.validate("input")
        self.assertEqual("Unknown Error", str(e2.exception))
        self.assertEqual("Boom!", str(e2.exception.errors[0][1]))

    def test_url(self):
        from configvalidator.validators import UrlValidator
        no_limits = UrlValidator()
        no_limits.validate("http://demo.tld")
        no_limits.validate("foo-bar")
        scheme = UrlValidator(scheme=["https"])
        scheme.validate("https://demo.tld")
        with self.assertRaises(ValidatorException) as e1:
            scheme.validate("http://demo.tld")
        self.assertEqual(str(e1.exception), "scheme not allowed")
        host = UrlValidator(hostname=["demo.tld"])
        host.validate("http://demo.tld")
        with self.assertRaises(ValidatorException) as e2:
            host.validate("http://demo2.tld")
        self.assertEqual(str(e2.exception), "host nor allowed")
        port = UrlValidator(port=[80])
        port.validate("http://demo.tld")
        port.validate("http://demo.tld:80")
        port.validate("https://demo.tld:80")
        with self.assertRaises(ValidatorException) as e3:
            port.validate("https://demo.tld")
        self.assertEqual(str(e3.exception), "port not allowed")
        with self.assertRaises(ValidatorException) as e4:
            port.validate("https://demo.tld:8080")
        self.assertEqual(str(e4.exception), "port not allowed")
        port2 = UrlValidator(port=[80], add_default_port=True)
        port2.validate("http://demo.tld")
        port2.validate("http://demo.tld:80")
        port2.validate("https://demo.tld:80")
        port2.validate("https://demo.tld")
        with self.assertRaises(ValidatorException) as e5:
            port.validate("https://demo.tld:8080")
        self.assertEqual(str(e5.exception), "port not allowed")
        port2.validate("ftp://demo.tld/path")
        port2.validate("ftp://demo.tld:21/path")
        with self.assertRaises(ValidatorException) as e6:
            port2.validate("ftp://demo.tld:50/path")
        self.assertEqual(str(e6.exception), "port not allowed")
        port3 = UrlValidator(add_default_port=True)
        port3.validate("http://demo.tld")
        port3.validate("http://demo.tld:80")
        with self.assertRaises(ValidatorException) as e7:
            port3.validate("https://demo.tld:80")
        self.assertEqual(str(e7.exception), "port not allowed")
        port4 = UrlValidator()
        port4.validate("http://demo.tld")
        port4.validate("http://demo.tld:80")
        port4.validate("https://demo.tld:80")

    def test_url_error(self):
        from configvalidator.validators import UrlValidator
        e = UrlValidator()
        with mock.patch('configvalidator.validators.urlparse') as m:
            m.side_effect = Exception('fooBar')
            with self.assertRaises(ValidatorException) as e1:
                e.validate("in")
            self.assertEqual(1, len(e1.exception.errors))
            error_msg, excp = e1.exception.errors[0]
            self.assertEquals('Unknown Error', error_msg)
            self.assertEquals("fooBar", str(excp))

    def test_email(self):
        from configvalidator.validators import EmailValidator
        no_limits = EmailValidator()
        no_limits.validate("test@sample.com")
        with self.assertRaises(ValidatorException) as e1:
            no_limits.validate("sample.com")
        self.assertEqual(str(e1.exception), "invalid email format")
        hostname = EmailValidator(hostname=["sample.com"])
        hostname.validate("test@sample.com")
        with self.assertRaises(ValidatorException) as e2:
            hostname.validate("test@sample.net")
        self.assertEqual(str(e2.exception), "invalid host")

    def test_or(self):
        from configvalidator.validators import OrValidator
        v = OrValidator(validators=[{
            "type": "int",
            "min": 10,
        }, {
            "type": "str",
            "min_length": 10,
        }])
        v.validate("10")
        with self.assertRaises(ValidatorException) as e1:
            v.validate("9")
        self.assertListEqual(
            sorted(e1.exception.info),
            sorted(["minimum: 10", "minimum string length: 10"])
        )
        with self.assertRaises(ValidatorException) as e2:
            v.validate("test")
        self.assertListEqual(
            sorted(e2.exception.info),
            sorted(["Input is no int", "minimum string length: 10"])
        )
        v.validate("test_12345")

    def test_or2(self):
        from configvalidator.validators import OrValidator
        v = OrValidator(validators=[{"type": "float"}, "int"])
        self.assertEqual("10.4", v.validate("10.4"))
        self.assertEqual("3", v.validate("3"))
        v2 = OrValidator(validators=[{"type": "float"}, "int"], kwargs={"min": 4})
        self.assertEqual("4", v.validate("4"))
        with self.assertRaises(ValidatorException) as e:
            v2.validate("3")
        self.assertListEqual(['minimum: 4', 'minimum: 4.0'], sorted(str(e.exception).split("\n")))

    def test_or3(self):
        from configvalidator.validators import OrValidator
        v = OrValidator(validators=[
            {"type": "str"},
        ], min_length=10)
        self.assertEqual("1234567890", v.validate("1234567890"))
        with self.assertRaises(ValidatorException) as e:
            v.validate("3")
        self.assertListEqual(['minimum string length: 10'], sorted(str(e.exception).split("\n")))

    def test_or_error(self):
        from configvalidator.validators import OrValidator, Validator
        from configvalidator.tools.basics import DATA_VALIDATOR

        def _(ins, val):
            raise Exception("error 123")
        type("DEMO_CLASS", (Validator,), {"validate": _})
        v = OrValidator(validators=["DEMO_CLASS"])
        with self.assertRaises(ValidatorException) as e:
            v.validate("")
        self.assertEqual(1, len(e.exception.errors))
        error_msg, excp = e.exception.errors[0]
        self.assertEquals('Unknown Error', error_msg)
        self.assertEquals("error 123", str(excp))
        del DATA_VALIDATOR["DEMO_CLASS"]

    def test_or_dep(self):
        from configvalidator.validators import OrValidator
        v = OrValidator(validators=[
            {"type": "bool"},
            {"type": "int"}
        ], int_max=10)
        self.assertEqual("true", v.validate("true"))
        self.assertEqual("3", v.validate("3"))
        with self.assertRaises(ValidatorException) as e:
            v.validate("11")
        self.assertListEqual(sorted(["allowed values: yes, no, y, n, true, false, t, f, 1, 0", "maximum: 10"]), sorted(str(e.exception).split("\n")))

    def test_and(self):
        from configvalidator.validators import AndValidator
        v = AndValidator(validators=[
            "int",
            "float"
        ],
            kwargs={
                "min": 10,
            })
        v.validate("10")
        with self.assertRaises(ValidatorException) as e1:
            v.validate("9")
        self.assertListEqual(
            sorted(e1.exception.info),
            sorted(["minimum: 10", "minimum: 10.0"])
        )
        with self.assertRaises(ValidatorException) as e2:
            v.validate("test")
        self.assertListEqual(
            sorted(e2.exception.info),
            sorted(["Input is no int", "Input is no float"])
        )

    def test_and_error(self):
        from configvalidator.validators import AndValidator, Validator
        from configvalidator.tools.basics import DATA_VALIDATOR

        def _(ins, val):
            raise Exception("error 123")
        type("DEMO_CLASS", (Validator,), {"validate": _})
        v = AndValidator(validators=["DEMO_CLASS"])
        with self.assertRaises(ValidatorException) as e:
            v.validate("")
        self.assertEqual(1, len(e.exception.errors))
        error_msg, excp = e.exception.errors[0]
        self.assertEquals('Unknown Error', error_msg)
        self.assertEquals("error 123", str(excp))
        del DATA_VALIDATOR["DEMO_CLASS"]

    def test_one_off(self):
        from configvalidator.validators import OneOffValidator
        v = OneOffValidator(validators=[{
            "type": "int",
            "min": 10,
        }, "empty"])
        self.assertEqual("", v.validate(""))
        self.assertEqual(40, v.validate("40"))
        with self.assertRaises(ValidatorException) as e:
            v.validate(" ")
        self.assertEqual("Input is no int\nThe input is not Empty.", str(e.exception))

    def test_one_off_errors(self):
        from configvalidator.validators import OneOffValidator
        from configvalidator.validators import Validator
        from configvalidator.tools.basics import DATA_VALIDATOR

        def _(ins, val):
            raise Exception("error 123")
        type("DEMO_CLASS", (Validator,), {"validate": _})
        v = OneOffValidator(validators=["DEMO_CLASS"])
        with self.assertRaises(ValidatorException) as e:
            v.validate("")
        self.assertEqual(1, len(e.exception.errors))
        error_msg, excp = e.exception.errors[0]
        self.assertEquals('Unknown Error', error_msg)
        self.assertEquals("error 123", str(excp))
        del DATA_VALIDATOR["DEMO_CLASS"]

    def test_ipv4(self):
        from configvalidator.validators import IPv4Validator
        no_limits = IPv4Validator()
        no_limits.validate("192.178.0.1")
        with self.assertRaises(ValidatorException) as e1:
            no_limits.validate("124.390.0.")
        self.assertEqual("invalid ipv4 format: [0-255] | no leading zeros", str(e1.exception))
        no_limits2 = IPv4Validator(cidr="/0")
        no_limits2.validate("192.178.0.1")
        private = IPv4Validator(private=True)
        private.validate("192.168.0.1")
        with self.assertRaises(ValidatorException) as e2:
            private.validate("1.1.1.1")
        self.assertEqual(
            str(e2.exception),
            "IP is not en private Network")
        network_valid = IPv4Validator(cidr="198.51.100.0/24")
        network_valid.validate("198.51.100.1")
        with self.assertRaises(ValidatorException) as e3:
            network_valid.validate("1.1.1.1")
        self.assertEqual(str(e3.exception), "IP outsite of subnet mask")

    def test_ipv4_error(self):
        from configvalidator.validators import IPv4Validator, IpValidator
        with self.assertRaises(InitException) as e1:
            IPv4Validator(cidr="123")
        self.assertEqual("cidr format error | IP/CIDR or /CIDR", str(e1.exception))
        with self.assertRaises(InitException) as e2:
            IPv4Validator(cidr="123.g.4./12")
        self.assertEqual("invalid ipv4 format: [0-255] | no leading zeros", str(e2.exception))
        # mock
        org_fn = IpValidator.validate_bits

        @staticmethod
        def _fail_fn(*args, **kwargs):
            raise Exception('FAIL')
        IpValidator.validate_bits = _fail_fn
        e = IPv4Validator()
        with self.assertRaises(ValidatorException) as e3:
            e.validate("1.1.1.1")
        self.assertEqual(1, len(e3.exception.errors))
        error_msg, excp = e3.exception.errors[0]
        self.assertEquals('Unknown Error', error_msg)
        self.assertEquals("FAIL", str(excp))
        # reset mock
        IpValidator.validate_bits = staticmethod(org_fn)
        self.assertTrue(isinstance(IpValidator.validate_bits, types.FunctionType))
        #
        with self.assertRaises(InitException) as e4:
            IPv4Validator(cidr="123.g/12")
        self.assertEqual("IP format: [0-255].[0-255].[0-255].[0-255]", str(e4.exception))

    def test_ipv6(self):
        from configvalidator.validators import Ipv6Validator
        no_limits = Ipv6Validator(cidr="/0")
        no_limits.validate("::192.178.0.1")
        no_limits.validate("2001:db8::8d3:0:0:0")
        v = Ipv6Validator()
        v.validate("::ffff:127.0.0.1")
        v.validate("::ffff:7f00:1")
        v.validate("2001:db8::8d3:0:0:0")
        v.validate("2001:0db8:0000:08d3:0000:8a2e:0070:7344")
        v.validate("2001:db8:0:8d3:0:8a2e:70:7344")
        v.validate("2001:db8::1428:57ab")
        v.validate("2001:0db8:0:0:0:0:1428:57ab")
        with self.assertRaises(ValidatorException) as e1:
            v.validate("22001:db8:0:0:8d3::")
        self.assertEqual(
            str(e1.exception),
            'invalid ipv6 syntax: each ipv6 block has maximum 16 bits')
        v.validate("2001:db8:0:0:8d3::")
        v.validate("2001:db8::8d3:0:0:0")
        with self.assertRaises(ValidatorException) as e2:
            v.validate("test")
        self.assertEqual(str(e2.exception), 'invalid ipv6 format')
        with self.assertRaises(ValidatorException) as e3:
            v.validate("2001:db8::8d3::")
        self.assertEqual(
            str(e3.exception),
            'invalid ipv6 syntax: only one reduction via ::')
        with self.assertRaises(ValidatorException) as e4:
            v.validate("2001:0db8:0:0:0:0:1428:57ab/128")
        self.assertEqual(
            str(e4.exception),
            "error: host subnet mask not allowed")
        host_subnet_mask = Ipv6Validator(host_subnet_mask=True)
        host_subnet_mask.validate("2001:0db8:0:0:0:0:1428:57ab/128")
        with self.assertRaises(ValidatorException) as e5:
            host_subnet_mask.validate("2001:0db8:0:0:0:0:1428:57ab/64")
        self.assertEqual(
            str(e5.exception),
            'if subnet mask is given it must be 128!')
        private = Ipv6Validator(private=True)
        private.validate("::1")
        private.validate("fdb7:bd47:e90f:23ce::1")
        private.validate("fe80::1")
        private.validate("febf::7645:6de2:ff:1")
        with self.assertRaises(ValidatorException) as e6:
            private.validate("2001:db8:0:8d3:0:8a2e:70:7344")
        self.assertEqual(
            str(e6.exception),
            'IP is not en private Network')

    def test_ipv6_error(self):
        from configvalidator.validators import Ipv6Validator, IpValidator
        with self.assertRaises(InitException) as e1:
            Ipv6Validator(cidr="::")
        self.assertEqual("cidr format error | IP/CIDR or /CIDR", str(e1.exception))
        with self.assertRaises(InitException) as e2:
            Ipv6Validator(cidr="127.0.0.1/12")
        self.assertEqual("invalid ipv6 format", str(e2.exception))
        # mock
        org_fn = IpValidator.validate_bits

        @staticmethod
        def _fail_fn(*args, **kwargs):
            raise Exception('FAIL ipv6')
        IpValidator.validate_bits = _fail_fn
        e = Ipv6Validator()
        with self.assertRaises(ValidatorException) as e3:
            e.validate("::")
        self.assertEqual(1, len(e3.exception.errors))
        error_msg, excp = e3.exception.errors[0]
        self.assertEquals('Unknown Error', error_msg)
        self.assertEquals("FAIL ipv6", str(excp))
        # reset mock
        IpValidator.validate_bits = staticmethod(org_fn)
        self.assertTrue(isinstance(IpValidator.validate_bits, types.FunctionType))
        #
        v1 = Ipv6Validator()
        with self.assertRaises(ValidatorException) as e4:
            v1.validate("2001:db8:0:8d3:0:8a2e:70:7344:2001:db8:0:8d3:0:8a2e:70:7344")
        self.assertEqual("invalid IPv6 address - just 8 blocks", str(e4.exception))

    def test_ip(self):
        from configvalidator.validators import IpValidator
        v = IpValidator()
        v.validate("192.178.0.1")
        v.validate("::ffff:127.0.0.1")
        with self.assertRaises(ValidatorException) as e1:
            self.assertFalse(v.validate("0.0.d.0"))
        self.assertListEqual(
            sorted(e1.exception.info),
            sorted(["invalid ipv4 format: [0-255] | no leading zeros", "invalid ipv6 format"])
        )

    def test_generalizedTime(self):
        from configvalidator.validators import GeneralizedTimeValidator
        v = GeneralizedTimeValidator()
        self.assertEqual(
            str(v.validate("20150613102908+0954")),
            "2015-06-13 10:29:08+09:54")
        self.assertEqual(str(v.validate("2015061310")), "2015-06-13 10:00:00")
        self.assertEqual(
            str(v.validate("2015061310Z")),
            "2015-06-13 10:00:00+00:00")
        self.assertEqual(
            str(v.validate("2015061310-0159")),
            "2015-06-13 10:00:00-01:59")
        self.assertEqual(
            str(v.validate("201506131012")),
            "2015-06-13 10:12:00")
        self.assertEqual(
            str(v.validate("20150613114513")),
            "2015-06-13 11:45:13")
        self.assertEqual(
            str(v.validate("20150613114513Z")),
            "2015-06-13 11:45:13+00:00")
        self.assertEqual(
            str(v.validate("20150613114513.111")),
            "2015-06-13 11:45:13.000111")
        self.assertEqual(
            str(v.validate("20150613114513.111Z")),
            "2015-06-13 11:45:13.000111+00:00")
        self.assertEqual(
            str(v.validate("20150613114313.121+0601")),
            "2015-06-13 11:43:13.000121+06:01")
        with self.assertRaises(ValidatorException) as e1:
            v.validate("2015061325")
        self.assertEqual(str(e1.exception), "hour must be in 0..23")
        with self.assertRaises(ValidatorException) as e2:
            v.validate("201506132361")
        self.assertEqual(str(e2.exception), "minute must be in 0..59")
        with self.assertRaises(ValidatorException) as e3:
            v.validate("20150613235960")
        self.assertEqual(str(e3.exception), "second must be in 0..59")
        with self.assertRaises(ValidatorException) as e4:
            v.validate("2015")
        self.assertEqual(
            str(e4.exception),
            "input: YYYYMMDDHH[MM[SS[.fff]]] | YYYYMMDDHH[MM[SS[.fff]]]Z | YYYYMMDDHH[MM[SS[.fff]]]+-HHMM")
        with self.assertRaises(ValidatorException) as e5:
            v.validate("2015131505")
        self.assertEqual(str(e5.exception), "month must be in 1..12")

    def test_generalizedTime_error(self):
        from configvalidator.validators import GeneralizedTimeValidator
        v = GeneralizedTimeValidator()
        with self.assertRaises(ValidatorException) as e1:
            v.validate("20150613114313.121&0601")
        self.assertEqual("input: YYYYMMDDHH[MM[SS[.fff]]] | YYYYMMDDHH[MM[SS[.fff]]]Z | YYYYMMDDHH[MM[SS[.fff]]]+-HHMM", str(e1.exception))


    def test_items(self):
        from configvalidator.validators import ItemsValidator
        items = ItemsValidator()
        res1 = items.validate("test")
        self.assertListEqual(["test"], res1)
        res2 = items.validate("test,  test2,test3")
        self.assertListEqual(["test", "test2", "test3"], res2)
        #
        items2 = ItemsValidator(strip=False, values=["test", " foo "])
        res3 = items2.validate(" foo ,test")
        self.assertListEqual(sorted(["test", " foo "]), sorted(res3))
        with self.assertRaises(ValidatorException) as e:
            items2.validate("foo")
        self.assertEqual("Element 'foo' ist not allowed: ['test', ' foo ']", str(e.exception))
        # min / max
        items3 = ItemsValidator(min=1, max=3, skip_empty=True)
        res4 = items3.validate("foo ,test")
        self.assertListEqual(sorted(["test", "foo"]), sorted(res4))
        with self.assertRaises(ValidatorException) as e2:
            items3.validate("")
        self.assertEqual("the allowed number (1) was not reached (0).", str(e2.exception))
        with self.assertRaises(ValidatorException) as e3:
            items3.validate("a,b,e,d")
        self.assertEqual("the allowed number (3) has been exceeded (4).", str(e3.exception))
        items4 = ItemsValidator(min=2)
        res5 = items4.validate("foo ,test,  ")
        self.assertListEqual(sorted(["test", "foo", ""]), sorted(res5))
        items5 = ItemsValidator(strip=False)
        self.assertListEqual(sorted(["test", "foo ", "  "]), sorted(items5.validate("foo ,test,  ")))

    def test_item(self):
        from configvalidator.validators import ItemValidator
        item = ItemValidator()
        self.assertEqual("test", item.validate("test"))
        self.assertEqual("test,  test", item.validate("test,  test"))

    def test_list(self):
        from configvalidator.validators import ListValidator
        lv = ListValidator()
        self.assertListEqual(sorted(["test", " foo", "bar"]), sorted(lv.validate('[\'test\', foo, "bar"]')))
        self.assertListEqual(["test"], lv.validate("test"))
        lv2 = ListValidator(strict=True)
        with self.assertRaises(ValidatorException) as e:
            lv2.validate("test")
        self.assertEqual("input list elements with [...]", str(e.exception))
        with self.assertRaises(ValidatorException) as e:
            lv2.validate("[test]")
        self.assertEqual("items must be surrounded by \" or '", str(e.exception))
        # empty list imput
        self.assertListEqual(sorted([]), sorted(lv.validate("    ")))
        self.assertListEqual(sorted([]), sorted(lv.validate("[]")))
        self.assertListEqual(sorted([" ", ""]), sorted(lv.validate("[ ,]")))

    def test_dict(self):
        from configvalidator.validators import DictValidator
        dv = DictValidator()
        self.assertDictEqual(dict(foo="bar"), dv.validate("{'foo':bar}"))
        self.assertDictEqual(dict(foo=" bar"), dv.validate("{foo: bar}"))
        self.assertDictEqual(dict(foo="bar"), dv.validate("{foo: \"bar\"}"))
        self.assertDictEqual(dict(foo="bar"), dv.validate("foo: \"bar\""))
        with self.assertRaises(ValidatorException) as e2:
            dv.validate("{'foo': \"bar\",foo:bar}")
        self.assertEqual("duplicate key input: foo", str(e2.exception))
        # strict mode
        sdv = DictValidator(strict=True)
        self.assertDictEqual(dict(foo="bar"), sdv.validate("{'foo': \"bar\"}"))
        with self.assertRaises(ValidatorException) as e1:
            sdv.validate("{'foo':bar}")
        self.assertEqual("items must be surrounded by \" or '", str(e1.exception))
        with self.assertRaises(ValidatorException) as e4:
            sdv.validate("'foo':bar")
        self.assertEqual("input dict elements with {...}", str(e4.exception))
        with self.assertRaises(ValidatorException) as e5:
            sdv.validate("{'foo': \"bar\",foobar}")
        self.assertEqual("items must be surrounded by \" or '", str(e5.exception))
        # duplicate_keys true
        ddkv = DictValidator(duplicate_keys=True)
        self.assertDictEqual(dict(foo="bar"), ddkv.validate("{'foo': \"bar\",foo:bar}"))
        with self.assertRaises(ValidatorException) as e3:
            ddkv.validate("{'foo': \"bar\",foobar}")
        self.assertEqual("key and values must be split by :", str(e3.exception))

    def test_dict_extend(self):
        from configvalidator.validators import DictValidator
        dv = DictValidator()
        self.assertDictEqual(dict(foo="bar", bla="ff,gg", val="  "), dv.validate("foo:bar,bla:\"ff,gg\",val:  "))
        self.assertDictEqual(dict(foo="bar", bla="ff,gg", val="  "), dv.validate("foo:bar,bla:\"ff,gg\",val:  ,"))
        with self.assertRaises(ValidatorException) as e1:
            dv.validate("bla:\"ff,gg\"foo:bar")
        self.assertEqual("Key-value pairs must be split by comma.", str(e1.exception))
        self.assertDictEqual({"test:": ""}, dv.validate("'test:':"))
        with self.assertRaises(ValidatorException) as e2:
            dv.validate("'test:'")
        self.assertEqual("key and values must be split by :", str(e2.exception))
        #
        edv = DictValidator()
        edv._DictValidator__key2 = re.compile(r"\s*(\"|')(?P<key>[^\1]*)\1{1}\s*(?P<rest>.*)")
        edv._DictValidator__val3 = re.compile(r"\s*(\"|')(?P<value>[^\1]*)\1{1}\s*(?P<rest>.*)")
        with self.assertRaises(ValidatorException) as e3:
            edv.validate("test")
        self.assertEqual("can not identify any dict key", str(e3.exception))
        with self.assertRaises(ValidatorException) as e4:
            edv.validate("'test': ")
        self.assertEqual("can not identify any dict value", str(e4.exception))
        # test sub dict
        self.assertDictEqual(dict(foo="bar", bla={}), dv.validate("foo:bar,bla: {},"))
        self.assertDictEqual(dict(foo="bar", bla=dict(foo="bar")), dv.validate("foo:bar,bla: {foo:bar}"))
        self.assertDictEqual(dict(foo="bar", bla="{foo:bar}"), dv.validate("foo:bar,bla: \"{foo:bar}\""))
        # and sub list
        self.assertDictEqual(dict(foo="bar", bla=[]), dv.validate("foo:bar,bla: [],"))
        self.assertDictEqual(dict(foo="bar", bla=["foo", "bar"]), dv.validate("foo:bar,bla: [foo,  \"bar\"],"))
        # double test
        self.assertDictEqual(dict(foo="bar", bla=dict(foo=dict(test="bar"))), dv.validate("foo:bar,bla: {foo: {test: \"bar\"}}"))
        with self.assertRaises(ValidatorException) as e5:
            dv.validate("foo:bar,bla: {foo: {test: \"bar\"}")
        self.assertEqual("opening brace but no closing", str(e5.exception))
        #
        org = DictValidator._find_relevant_sub_string

        def _(*args, **kwargs):
            return None, None
        DictValidator._find_relevant_sub_string = staticmethod(_)
        with self.assertRaises(ValidatorException) as e6:
            dv._add_sub_item(sub_type=".", item="")
        self.assertEqual("unsupported type: .", str(e6.exception))
        DictValidator._find_relevant_sub_string = staticmethod(org)

    def test_netbios(self):
        from configvalidator.validators import NetBIOSValidator
        v = NetBIOSValidator()
        v.validate("test")
        with self.assertRaises(ValidatorException) as e1:
            v.validate("1234567890123456")
        self.assertEqual("maximum NetBIOS Name length: 15", str(e1.exception))
        with self.assertRaises(ValidatorException) as e2:
            v.validate("")
        self.assertEqual("minimum NetBIOS Name length: 1", str(e2.exception))
        with self.assertRaises(ValidatorException) as e3:
            v.validate(".test")
        self.assertTrue(str(e3.exception).startswith("the fisrt character must be one of: "))
        with self.assertRaises(ValidatorException) as e4:
            v.validate("test=|")
        self.assertTrue(str(e4.exception).startswith("allowed characters: "))
        
    def test_StripQuotationMark(self):
        from configvalidator.validators import StripQuotationMark
        s = StripQuotationMark(validator_name="int")
        self.assertEqual(0, s.validate("0"))
        self.assertEqual(0, s.validate("\"0\""))
        s1 = StripQuotationMark(validator_name="int", force_strip=True)
        with self.assertRaises(ValidatorException) as e:
            self.assertEqual(1, s1.validate("1"))
        self.assertEqual("can not strip quotation mark - input len must be at least 2!", str(e.exception))
        self.assertEqual(1, s1.validate("\"1\""))
        self.assertEqual(10, s1.validate("'10'"))
        s2 = StripQuotationMark(validator_name="int", output_quotation_mark=True)
        self.assertEqual("'10'", s2.validate("'10'"))
        
    def test_StripQuotationMarkPathValidator(self):
        from configvalidator.validators import StripQuotationMarkPathValidator
        #StripQuotationMarkPathValidator = load_validator("strip_path")
        no_limits = StripQuotationMarkPathValidator()
        no_limits.validate(os.path.join(testutils.get_test_utils_base(), "data", "exist"))
        no_limits.validate("'" + os.path.join(testutils.get_test_utils_base(), "data", "exist") + "'")
        no_limits.validate('"' + os.path.join(testutils.get_test_utils_base(), "data", "exist") + '"')
        absolute = StripQuotationMarkPathValidator(absolute=True)
        self.assertEqual(os.path.dirname(__file__), absolute.validate(os.path.dirname(__file__)))
        self.assertEqual("'" + os.path.dirname(__file__) +  "'", absolute.validate("'" + os.path.dirname(__file__) +  "'"))
        self.assertEqual('"' + os.path.dirname(__file__) + '"', absolute.validate('"' + os.path.dirname(__file__) + '"'))


if __name__ == '__main__':
    unittest.main()
