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
from configvalidator.tools.configValidator import ParseObj
from configvalidator import load_validator
from configvalidator.tools.basics import Validator
from configvalidator.validators import DefaultValidator, ErrorValidator
from configvalidator import ParserException


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.cp = testutils.CPStub4()
        self.parser = ParseObj(cp=self.cp)
        self.default_val = load_validator("default")
        # error validator

        def _i(self, *args, **kwargs):
            super(self.__class__, self).__init__(error_msg="my - error")
        self.error_val = type("my_ERROR", (ErrorValidator,), {"__init__": _i})
        # define validator

        def _(self, *args, **kwargs):
            pass
        self.dep_val = type("DEMO_CLASS", (DefaultValidator,), {"__init__": _})

    def tearDown(self):
        from configvalidator.tools.basics import DATA_VALIDATOR
        del DATA_VALIDATOR["DEMO_CLASS"]

    def test_default(self):
        self.cp.add("test", "item", "1")
        self.parser.current_section = "test"
        self.parser.current_option = "item"
        self.parser.add_value(validator_class=self.default_val, validator_init_dict={})
        self.parser.current_section = None
        self.parser.current_option = None
        res = self.parser.result()
        self.assertEqual(1, len(res))
        self.assertEqual(1, len(res.test))
        self.assertEqual("1", res.test.item)

    def test_add_twice(self):
        self.cp.add("test", "item", "1")
        self.parser.current_section = "test"
        self.parser.current_option = "item"
        self.parser.add_value(validator_class=self.default_val, validator_init_dict={})
        self.cp.add("test", "item", "2")
        self.assertEqual("2", self.cp.get("test", "item"))
        self.parser.add_value(validator_class=self.default_val, validator_init_dict={})
        self.parser.current_section = None
        self.parser.current_option = None
        res = self.parser.result()
        self.assertEqual(1, len(res))
        self.assertEqual(1, len(res.test))
        self.assertEqual("2", res.test.item)

    def test_dependencies(self):
        # add item1
        self.cp.add("test", "item1", "1")
        self.parser.current_section = "test"
        self.parser.current_option = "item1"
        self.parser.add_value(validator_class=self.dep_val,
                              validator_init_dict=dict(a=("test", "item2")),
                              dependencies_list=["a"])
        # check result --> error item2 missing
        with self.assertRaises(ParserException) as e:
            self.parser.current_section = None
            self.parser.current_option = None
            self.parser.result()
        self.assertEqual("not all dependencies resolved: 'test'/'item1'", str(e.exception))
        # add item2
        self.cp.add("test", "item2", "2")
        self.parser.current_section = "test"
        self.parser.current_option = "item2"
        self.parser.add_value(validator_class=self.dep_val, validator_init_dict={})
        # get result
        self.parser.current_section = None
        self.parser.current_option = None
        res = self.parser.result()
        self.assertEqual(1, len(res))
        self.assertEqual(2, len(res.test))
        self.assertEqual("1", res.test.item1)
        self.assertEqual("2", res.test.item2)

    def test_dependencies_2(self):
        # item2
        self.cp.add("test", "item2", "2")
        self.parser.current_section = "test"
        self.parser.current_option = "item2"
        self.parser.add_value(validator_class=self.dep_val, validator_init_dict={})
        # item1
        self.parser.current_section = "test"
        self.parser.current_option = "item1"
        self.cp.add("test", "item1", "1")
        self.parser.add_value(validator_class=self.dep_val,
                              validator_init_dict=dict(a=("test", "item2")),
                              dependencies_list=["a"])
        # get result
        self.parser.current_section = None
        self.parser.current_option = None
        res = self.parser.result()
        self.assertEqual(1, len(res))
        self.assertEqual(2, len(res.test))
        self.assertEqual("1", res.test.item1)
        self.assertEqual("2", res.test.item2)

    def test_dependencies_complex_2(self):
        # test -> item1
        self.parser.current_section = "test"
        self.parser.current_option = "item1"
        self.cp.add("test", "item1", "1")
        self.parser.add_value(validator_class=self.dep_val,
                              validator_init_dict=dict(a=("test", "item2"), b=("foo", "item1")),
                              dependencies_list=["a", "b"])
        # teswt -> item2
        self.cp.add("test", "item2", "2")
        self.parser.current_section = "test"
        self.parser.current_option = "item2"
        self.parser.add_value(validator_class=self.dep_val,
                              validator_init_dict=dict(a=("foo", "item1"), b=("foo", "item2")),
                              dependencies_list=["a", "b"])
        # foo -> item1
        self.cp.add("foo", "item1", "3")
        self.parser.current_section = "foo"
        self.parser.current_option = "item1"
        self.parser.add_value(validator_class=self.dep_val,
                              validator_init_dict=dict(c=("foo", "item2")),
                              dependencies_list=["c"])
        # foo -> item1
        self.cp.add("foo", "item2", "4")
        self.parser.current_section = "foo"
        self.parser.current_option = "item2"
        self.parser.add_value(validator_class=self.dep_val,
                              validator_init_dict=dict(val=("bar", "item1")),
                              dependencies_list=["val"])
        # bar -> item1
        self.cp.add("bar", "item1", "5")
        self.parser.current_section = "bar"
        self.parser.current_option = "item1"
        self.parser.add_value(validator_class=self.dep_val,
                              validator_init_dict={})
        # get result
        self.parser.current_section = None
        self.parser.current_option = None
        res = self.parser.result()
        self.assertEqual(3, len(res))
        self.assertEqual(2, len(res.test))
        self.assertEqual("1", res.test.item1)
        self.assertEqual("2", res.test.item2)
        self.assertEqual(2, len(res.foo))
        self.assertEqual("3", res.foo.item1)
        self.assertEqual("4", res.foo.item2)
        self.assertEqual(1, len(res.bar))
        self.assertEqual("5", res.bar.item1)

    def test_dependencies_validate_error(self):
        # add item1
        self.cp.add("test", "item1", "1")
        self.parser.current_section = "test"
        self.parser.current_option = "item1"
        self.parser.add_value(validator_class=self.error_val,
                              validator_init_dict=dict(a=("test", "item2")),
                              dependencies_list=["a"])
        # add item2
        self.cp.add("test", "item2", "2")
        self.parser.current_section = "test"
        self.parser.current_option = "item2"
        self.parser.add_value(validator_class=self.dep_val, validator_init_dict={})
        # get result
        self.parser.current_section = None
        self.parser.current_option = None
        with self.assertRaises(ParserException) as e:
            self.parser.result()
        error_msg, dep_msg = str(e.exception).split("\n")
        self.assertEqual("error validating [test]item1: my - error", error_msg)
        self.assertEqual("not all dependencies resolved: 'test'/'item1'", dep_msg)


if __name__ == '__main__':
    unittest.main()
