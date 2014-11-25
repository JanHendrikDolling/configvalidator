# -*- coding: utf-8 -*-
'''
Created on 23.03.2014

@author: dolling
'''
import os
import sys
import imp
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from configvalidator import ConfigValidator
from configvalidator import ConfigValidatorException
from configvalidator import Validator
from configvalidator import Feature
import configvalidator.configvalidator as cv_to_mock
import mock


base = os.path.dirname(__file__)


class Test(unittest.TestCase):

    def test_1a(self):
        c = {
            "Test": {
                "t1": {
                    "default": "127.0.0.1",
                    "validator": "TRUE",
                },
                "t2": {
                    "default": "wert",
                    "validator": "TRUE",
                },
            }
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(2, len(conf.Test))
        self.assertEqual("127.0.0.1", conf.Test.t1)
        self.assertEqual("wert", conf.Test.t2)

    def test_1b(self):
        c = {
            "Test": {
                "t1": {
                    "default": "127.0.0.1",
                },
            }
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    '"validator" or "return" required for [Test]->t1')
                raise

    def test_1c(self):
        c = {
            "Test": {
                "t1": {
                    "validator": "TRUE",
                },
            }
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(str(e), "[Test][t1] not in ini file")
                raise

    def test_1d(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_section": "Standard_Profils",
                    "LIST_INPUT_return": lambda x: int(x),
                    "LIST_INPUT_exit_on_error": True,
                    "default": "False",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual(None, conf.Test.t1)

    def test_1e(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_return": lambda x: int(x),
                    "LIST_INPUT_exit_on_error": True,
                    "default": "False",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Feature "LIST_INPUT" required entry "LIST_INPUT_section" for [Test]->t1')
                raise

    def test_1f(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_section": "Standard_Profils",
                    "LIST_INPUT_exit_on_error": True,
                    "default": "False",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    '"LIST_INPUT_validator" or "LIST_INPUT_return" required for [Test]->t1')
                raise

    def test_1g(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_section": "Standard_Profils",
                    "LIST_INPUT_return": lambda x: int(x),
                    "default": "False",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Feature "LIST_INPUT" required entry "LIST_INPUT_exit_on_error" for [Test]->t1')
                raise

    def test_2a(self):
        c = {
            "Test": {
                "t1": {
                    "validator": "INT",
                },
            }
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "2.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Validator "INT" with input "Hallo" return False for [Test]->t1')
                raise

    def test_2b(self):
        c = {
            "Test": {
                "t1": {
                    "validator": "TRUE",
                },
                "t2": {
                    "default": "wert",
                    "validator": "TRUE",
                },
            }
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "2.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(2, len(conf.Test))
        self.assertEqual("Hallo", conf.Test.t1)
        self.assertEqual("wert", conf.Test.t2)

    def test_2c(self):
        c = {
            "Test": {
                "t1": {
                    "return": lambda x: int(x),
                },
            }
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "2.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Validator "ReturnValidator(<lambda>)" with input "Hallo" return False for [Test]->t1')
                raise

    def test_2d(self):
        c = {
            "Test": {
                "t1": {
                    "validator": "TRUE",
                },
                "t2": {
                    "default": "wert",
                    "return": lambda x: int(x),
                },
            }
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "2.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Validator "ReturnValidator(<lambda>)" with input "wert" return False for [Test]->t2')
                raise

    def test_3a(self):
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "config.ini"),
                    ini_validator=None)
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'parameter ini_validator must be a dict')
                raise

    def test_3b(self):
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "config.ini")).parse()
        self.assertEqual(conf, {})

    def test_3c(self):
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(ini_path=os.path.join(base, "no_file.ini"))
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    "no file @ {0}".format(
                        os.path.join(
                            base,
                            "no_file.ini")))
                raise

    def test_4a(self):

        class Demo(Validator):
            name = "DEMO"

            def validate(self, value):
                try:
                    self.transform(value)
                    return True
                except:
                    return False

            def transform(self, value):
                return value
        c = {
            "Test": {
                "t1": {
                    "validator": "DEMO",
                },
            }
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "2.ini"),
            ini_validator=c).parse()
        self.assertEqual("Hallo", conf.Test.t1)
        self.assertEqual(1, len(conf.Test))

    def test_4b(self):
        c = {
            "Test": {
                "t1": {
                    "validator": "DEMO2",
                },
            }
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "2.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'No Validator with name DEMO2 for [Test]->t1')
                raise

    def test_4c(self):
        with self.assertRaises(ConfigValidatorException):
            try:
                class Demo(Validator):
                    name = "TRUE"

                    def validate(self, value):
                        try:
                            self.transform(value)
                            return True
                        except:
                            return False

                    def transform(self, value):
                        return value
            except ConfigValidatorException as e:
                self.assertEqual(str(e), 'duplicate validator name TRUE')
                raise

    def test_4d(self):
        class Demo(Validator):
            name = "DEMO3"
            inaktiv = True

            def validate(self, value):
                try:
                    self.transform(value)
                    return True
                except:
                    return False

            def transform(self, value):
                return value
        c = {
            "Test": {
                "t1": {
                    "validator": "DEMO3",
                },
            }
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "2.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'No Validator with name DEMO3 for [Test]->t1')
                raise

    def test_5a(self):
        c = {
            "Test": {
                "t1": {
                    "default": "127.0.0.1",
                    "validator": "OR",
                },
            }
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Validator "OR" required entry "validator_OR" for [Test]->t1')
                raise

    def test_5b(self):
        c = {
            "Test": {
                "t1": {
                    "default": "127.0.0.1",
                    "validator": "OR",
                    "validator_OR": ["TRUE", "INT"],
                },
            }
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual("127.0.0.1", conf.Test.t1)

    def test_5c(self):
        c = {
            "Test": {
                "t1": {
                    "default": "127.0.0.1",
                    "validator": "OR",
                    "validator_OR": ["FILE", "INT"],
                },
            }
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Validator "OR" with input "127.0.0.1" return False for [Test]->t1')
                raise

    def test_5d(self):
        c = {
            "Test": {
                "t1": {
                    "default": "127.0.0.1",
                    "validator": "OR",
                    "validator_OR": ["TRUE", "ERROR"],
                },
            }
        }

        class Demo(Validator):
            name = "ERROR"

            def __init__(self, val):
                super(Demo, self).__init__()

            def validate(self, value):
                pass

            def transform(self, value):
                return value
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'validator_OR: can not instance Validator "ERROR" [no method __init__(self)] for [Test]->t1')
                raise

    def test_6a(self):
        a = {
            "Test": {
                "t1": {
                    "default": "A",
                    "validator": "TRUE",
                },
            }
        }
        b = {
            "Test": {
                "t1": {
                    "default": "B",
                    "validator": "TRUE",
                },
            }
        }
        val_a = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=a)
        val_b = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=b)
        conf_a = val_a.parse()
        conf_b = val_b.parse()
        self.assertEqual(1, len(conf_a))
        self.assertEqual(1, len(conf_a.Test))
        self.assertEqual("A", conf_a.Test.t1)
        self.assertEqual(1, len(conf_b))
        self.assertEqual(1, len(conf_b.Test))
        self.assertEqual("B", conf_b.Test.t1)

    def test_6b(self):
        a = {
            "Test": {
                "t1": {
                    "default": "A",
                    "validator": "TRUE",
                },
            }
        }
        b = {
            "Test": {
                "t1": {
                    "default": "B",
                    "validator": "TRUE",
                },
            }
        }
        c = {
            "Test": {
                "t1": {
                    "default": "C",
                    "validator": "TRUE",
                },
            }
        }
        val_a = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=a)
        val_b = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=b)
        val_c = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c)
        conf_b = val_b.parse()
        conf_a = val_a.parse()
        conf_c = val_c.parse()
        self.assertEqual(1, len(conf_a))
        self.assertEqual(1, len(conf_a.Test))
        self.assertEqual("A", conf_a.Test.t1)
        self.assertEqual(1, len(conf_b))
        self.assertEqual(1, len(conf_b.Test))
        self.assertEqual("B", conf_b.Test.t1)
        self.assertEqual(1, len(conf_c))
        self.assertEqual(1, len(conf_c.Test))
        self.assertEqual("C", conf_c.Test.t1)

    def test_7a(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "F1",
                },
            }
        }

        class Demo(Feature):
            name = "F1"

            def execute(self):
                return "ABC"
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual("ABC", conf.Test.t1)

    def test_7b(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "F2",
                },
            }
        }

        class Demo(Feature):
            name = "F2"

            @classmethod
            def required_records(cls):
                return ["foo"]

            def execute(self):
                pass
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Feature "F2" required entry "foo" for [Test]->t1')
                raise

    def test_7c(self):
        
        with self.assertRaises(ConfigValidatorException):
            try:
                class Demo2(Feature):
                    name = "EI1"
        
                    def execute(self):
                        pass
                imp.load_source("feature", os.path.join(os.path.dirname(__file__), "feature.py"))
            except ConfigValidatorException as e:
                self.assertEqual(str(e), 'duplicate feature name EI1')
                raise

    def test_7d(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "F5",
                    "foo": "bar"
                },
            }
        }

        class Demo(Feature):
            name = "F5"

            @classmethod
            def required_records(cls):
                return ["foo"]

            def execute(self):
                return self._get_dict()["foo"]
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual("bar", conf.Test.t1)

    def test_7e(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "NO_FEATURE",
                },
            }
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'No Feature with name NO_FEATURE for [Test]->t1')
                raise

    def test_7f(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "FV1",
                },
            }
        }

        class Demo(Feature, Validator):
            name = "FV1"

            @classmethod
            def required_records(cls):
                return ["foo"]

            def execute(self):
                pass

            def validate(self, value):
                pass

            def transform(self, value):
                pass
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Validator/Feature "FV1" required entry "foo" for [Test]->t1')
                raise
            
    def test_7g(self):
        with self.assertRaises(ConfigValidatorException):
            try:
                class Demo2(Validator):
                    name = "EV2"
                
                    def validate(self, value):
                        return True
                
                    def transform(self, value):
                        return value
                imp.load_source("validator2", os.path.join(os.path.dirname(__file__), "validator2.py"))
            except ConfigValidatorException as e:
                self.assertEqual(str(e), 'duplicate validator name EV2')
                raise

    def test_8a(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_section": "Standard_Profils",
                    "LIST_INPUT_return": lambda x: int(x),
                    "LIST_INPUT_exit_on_error": False,
                    "default": "True",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual(0, len(conf.Test.t1))
        self.assertEqual({}, conf.Test.t1)

    def test_8b(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_section": "Standard_Profils",
                    "LIST_INPUT_return": lambda x: int(x),
                    "LIST_INPUT_exit_on_error": True,
                    "default": "True",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(str(e), 'No Section: Standard_Profils')
                raise

    def test_9a(self):
        c = {
            "Test": {
                "t1": {
                    "return": "Fail",
                },
            }
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "2.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    '"return" for [Test]->t1 must be a Function')
                raise

    def test_10a(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_section": "Standard_Profils",
                    "LIST_INPUT_return": lambda x: int(x),
                    "LIST_INPUT_exit_on_error": False,
                    "default": "False",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "10.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual(2, len(conf.Test.t1))
        self.assertEqual(10, conf.Test.t1.a)
        self.assertEqual(4, conf.Test.t1.b)

    def test_10b(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_section": "Standard_Profils",
                    "LIST_INPUT_validator": "INT",
                    "LIST_INPUT_exit_on_error": False,
                    "default": "False",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "10.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual(2, len(conf.Test.t1))
        self.assertEqual(10, conf.Test.t1.a)
        self.assertEqual(4, conf.Test.t1.b)

    def test_10c(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_section": "Standard_Profils",
                    "LIST_INPUT_return": lambda x: int(x),
                    "LIST_INPUT_exit_on_error": True,
                    "default": "False",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "10.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    '[Test][t1] validation error at index "c" with input "Hallo"')
                raise

    def test_10d(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_section": "Standard_Profils",
                    "LIST_INPUT_exit_on_error": False,
                    "default": "False",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "10.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    '"LIST_INPUT_validator" or "LIST_INPUT_return" required for [Test]->t1')
                raise

    def test_10e(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_return": lambda x: int(x),
                    "LIST_INPUT_exit_on_error": False,
                    "default": "False",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "10.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Feature "LIST_INPUT" required entry "LIST_INPUT_section" for [Test]->t1')
                raise

    def test_10f(self):
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_section": "Standard_Profils",
                    "LIST_INPUT_validator": "INT",
                    "LIST_INPUT_exit_on_error": True,
                    "default": "False",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "10.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    '[Test][t1] validation error at index "c" with input "Hallo"')
                raise

    def test_10g(self):
        class Demo(Validator):
            name = "EXCEPTION"

            def validate(self, value):
                raise Exception("foo")

            def transform(self, value):
                return value
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_section": "Standard_Profils",
                    "LIST_INPUT_validator": "EXCEPTION",
                    "LIST_INPUT_exit_on_error": True,
                    "default": "False",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "10.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertTrue(str(e) in [
                    '[Test][t1] Exception at a | msg: foo',
                    '[Test][t1] Exception at b | msg: foo',
                    '[Test][t1] Exception at c | msg: foo',
                ])
                raise

    def test_10h(self):
        class Demo(Validator):
            name = "EXCEPTION2"

            def validate(self, value):
                raise Exception("foo")

            def transform(self, value):
                return value
        c = {
            "Test": {
                "t1": {
                    "feature": "LIST_INPUT",
                    "LIST_INPUT_section": "Standard_Profils",
                    "LIST_INPUT_validator": "EXCEPTION2",
                    "LIST_INPUT_exit_on_error": False,
                    "default": "False",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "10.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual({}, conf.Test.t1)

    def test_11a(self):
        c = {
            "A": {
                "b": {
                    "feature": "SUB_INI",
                    "SUB_INI_config": {
                        "Test": {
                            "t1": {
                                "validator": "TRUE",
                            },
                        }
                    },
                    "default": "",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "11.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.A))
        self.assertEqual(1, len(conf.A.b))
        self.assertEqual(1, len(conf.A.b.Test))
        self.assertEqual("Hallo", conf.A.b.Test.t1)

    def test_11b(self):
        c = {
            "A": {
                "b": {
                    "feature": "SUB_INI",
                    "SUB_INI_config": {
                        "Test": {
                            "t1": {
                                "validator": "TRUE",
                            },
                        }
                    },
                    "default": "2.ini",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.A))
        self.assertEqual(1, len(conf.A.b))
        self.assertEqual(1, len(conf.A.b.Test))
        self.assertEqual("Hallo", conf.A.b.Test.t1)

    def test_11c(self):
        c = {
            "A": {
                "b": {
                    "feature": "SUB_INI",
                    "SUB_INI_config": {
                        "Test": {
                            "t1": {
                                "validator": "TRUE",
                            },
                        }
                    },
                    "default": None,
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.A))
        self.assertEqual(None, conf.A.b)

    def test_11c_2(self):
        c = {
            "A": {
                "b": {
                    "feature": "SUB_INI",
                    "SUB_INI_config": {
                        "Test": {
                            "t1": {
                                "validator": "TRUE",
                            },
                        }
                    },
                    "default": "",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.A))
        self.assertEqual(None, conf.A.b)

    def test_11d(self):
        c = {
            "A": {
                "b": {
                    "feature": "SUB_INI",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "11.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Feature "SUB_INI" required entry "SUB_INI_config" for [A]->b')
                raise

    def test_11e(self):
        c = {
            "A": {
                "b": {
                    "feature": "SUB_INI",
                    "SUB_INI_config": {
                        "Test": {
                            "t1": {
                                "validator": "TRUE",
                            },
                        }
                    },
                    "default": "no_file.ini",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    "SUB_INI for [A]->b | msg: no file @ {0}".format(
                        os.path.join(
                            base,
                            "no_file.ini")))
                raise

    def test_12a(self):
        c = {
            "Eintrag": {
                "info": {
                    "validator": "STRING",
                },
                "wert": {
                    "validator": "INT",
                },
                "json": {
                    "validator": "JSON",
                    "transform": False,
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "12.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(3, len(conf.Eintrag))
        self.assertEqual("Test", conf.Eintrag.info)
        self.assertEqual(20, conf.Eintrag.wert)
        self.assertEqual('{"a": [1, 2, 3] }', conf.Eintrag.json)

    def test_12b(self):
        c = {
            "Eintrag": {
                "info": {
                    "validator": "STRING",
                },
                "wert": {
                    "validator": "INT",
                    "transform": False,
                },
                "json": {
                    "validator": "JSON",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "12.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(3, len(conf.Eintrag))
        self.assertEqual("Test", conf.Eintrag.info)
        self.assertEqual("20", conf.Eintrag.wert)
        self.assertEqual(1, len(conf.Eintrag.json))
        self.assertEqual([1, 2, 3], conf.Eintrag.json.a)

    def test_13a(self):
        c = {
            "A": {
                "B": {
                    "validator": "EMAIL",
                    "default": "test@test.de",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.A))
        self.assertEqual("test@test.de", conf.A.B)

    def test_13b(self):
        c = {
            "A": {
                "B": {
                    "validator": "EMAIL",
                    "default": "testtest.de",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    "Validator \"EMAIL\" with input \"testtest.de\" return False for [A]->B".format(
                        os.path.join(
                            base,
                            "no_file.ini")))
                raise

    def test_13c(self):
        c = {
            "A": {
                "B": {
                    "validator": "EMAIL",
                    "default": "test@test.de",

                    "EMAIL_method": "regex",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.A))
        self.assertEqual("test@test.de", conf.A.B)

    def test_13d(self):
        c = {
            "A": {
                "B": {
                    "validator": "EMAIL",
                    "default": "testtest.de",
                    "EMAIL_method": "regex",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    "Validator \"EMAIL\" with input \"testtest.de\" return False for [A]->B")
                raise

    def test_14a(self):
        c = {
            "A": {
                "B": {
                    "validator": "EMAIL",
                    "default": "test@test.de",
                    "EMAIL_method": "parseaddr",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.A))
        self.assertEqual("test@test.de", conf.A.B)

    def test_14b(self):
        c = {
            "A": {
                "B": {
                    "validator": "EMAIL",
                    "default": "testtest.de",
                    "EMAIL_method": "parseaddr",
                },
            },
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.A))
        self.assertEqual("testtest.de", conf.A.B)

    def test_14c(self):
        c = {
            "A": {
                "B": {
                    "validator": "EMAIL",
                    "default": "[invalid!email]",
                    "EMAIL_method": "parseaddr",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    "Validator \"EMAIL\" with input \"[invalid!email]\" return False for [A]->B")
                raise

    def test_15a(self):
        c = {
            "A": {
                "B": {
                    "validator": "EMAIL",
                    "default": "ffff@dd.dd",
                    "EMAIL_method": "FAIL",
                },
            },
        }
        with self.assertRaises(ConfigValidatorException):
            try:
                ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'no Email Validator method "FAIL" for [A]->B')
                raise

    def testName1(self):
        cv = ConfigValidator(ini_path=os.path.join(base, "config.ini"),
                             ini_validator={
            "fooo": {
                "bar": {
                    "return": lambda x: "blaa",
                    "default": "cxxss"
                },
            },
        })
        data = cv.parse()
        self.assertEquals(data.fooo.bar, "blaa")

    def testName2(self):
        cv = ConfigValidator(ini_path=os.path.join(base, "config.ini"),
                             ini_validator={
            "fooo": {
                "bar": {
                    "validator": "STRING",
                    "default": "test123"
                },
            },
        })
        data = cv.parse()
        self.assertEquals(data.fooo.bar, "test123")

    def testName3(self):
        cv = ConfigValidator(ini_path=os.path.join(base, "config.ini"),
                             ini_validator={
            "fooo": {
                "bar": {
                    "validator": "INT",
                    "default": "45"
                },
            },
        })
        data = cv.parse()
        self.assertEquals(data.fooo.bar, 45)

    def testName4(self):
        cv = ConfigValidator(ini_path=os.path.join(base, "config.ini"),
                             ini_validator={
            "fooo": {
                "bar": {
                    "validator": "TRUE",
                    "default": "45"
                },
            },
        })
        data = cv.parse()
        self.assertEquals(data.fooo.bar, "45")

    def testName5(self):
        cv = ConfigValidator(ini_path=os.path.join(base, "config.ini"),
                             ini_validator={
            "fooo": {
                "bar": {
                    "validator": "JSON",
                    "default": "{\"a\": [1, 2, 3] }"
                },
            },
        })
        data = cv.parse()
        self.assertEquals(data.fooo.bar.a, [1, 2, 3])

    def testName6(self):
        cv = ConfigValidator(
            ini_path=os.path.join(
                base,
                "10.ini"),
            ini_validator={
                "Test": {
                    "t1": {
                        "feature": "LIST_INPUT",
                        "LIST_INPUT_section": "Standard_Profils",
                        "LIST_INPUT_return": lambda x: int(x),
                        "LIST_INPUT_exit_on_error": False,
                    },
                },
            })
        data = cv.parse()
        self.assertEquals(data.Test.t1.a, 10)
        self.assertEquals(data.Test.t1.b, 4)

    def testName7(self):
        cv = ConfigValidator(
            ini_path=os.path.join(
                base,
                "11.ini"),
            ini_validator={
                "A": {
                    "b": {
                        "feature": "SUB_INI",
                        "SUB_INI_config": {
                            "Test": {
                                "t1": {
                                    "validator": "TRUE",
                                },
                            }},
                    },
                },
            })
        conf = cv.parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.A))
        self.assertEqual(1, len(conf.A.b))
        self.assertEqual(1, len(conf.A.b.Test))
        self.assertEqual("Hallo", conf.A.b.Test.t1)

    def test_import_a(self):
        from configvalidator import TrueValidator
        with self.assertRaises(ConfigValidatorException):
            try:
                TrueValidator()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'instance error - create instance via enviroment get_instance method')
                raise

    def test_import_b(self):
        from configvalidator import IntValidator
        with self.assertRaises(ConfigValidatorException):
            try:
                IntValidator()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'instance error - create instance via enviroment get_instance method')
                raise

    def test_import_c(self):
        from configvalidator import BoolValidator
        with self.assertRaises(ConfigValidatorException):
            try:
                BoolValidator()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'instance error - create instance via enviroment get_instance method')
                raise

    def test_import_d(self):
        from configvalidator import JsonValidator
        with self.assertRaises(ConfigValidatorException):
            try:
                JsonValidator()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'instance error - create instance via enviroment get_instance method')
                raise

    def test_import_e(self):
        from configvalidator import StringValidator
        with self.assertRaises(ConfigValidatorException):
            try:
                StringValidator()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'instance error - create instance via enviroment get_instance method')
                raise

    def test_import_f(self):
        from configvalidator import OrValidator
        with self.assertRaises(ConfigValidatorException):
            try:
                OrValidator()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'instance error - create instance via enviroment get_instance method')
                raise

    def test_import_g(self):
        from configvalidator import FileValidator
        with self.assertRaises(ConfigValidatorException):
            try:
                FileValidator()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'instance error - create instance via enviroment get_instance method')
                raise

    def test_new_a(self):
        from configvalidator.configvalidator import Entry
        with self.assertRaises(ConfigValidatorException):
            try:
                Entry.__new__(Entry)
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'instance error - create instance via enviroment get_instance method')
                raise

    def test_exception_1a(self):
        class Test(object):
            pass
        c = {
            "Test": {
                "t1": {
                    "feature": Test,
                },
            }
        }
        conf = ConfigValidator(
            ini_path=os.path.join(
                base,
                "1.ini"),
            ini_validator=c)
        with self.assertRaises(ConfigValidatorException):
            try:
                conf.env.section = "Test"
                conf.env.option = "t1"
                conf.env.get_feature()
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Test must be a subclass from Feature')
                raise

    def test_exception_1b(self):
        class Test(object):
            pass
        conf = ConfigValidator(ini_path=os.path.join(base, "config.ini"))
        with self.assertRaises(ConfigValidatorException):
            try:
                conf.env.load_validator(Test)
            except ConfigValidatorException as e:
                self.assertEqual(
                    str(e),
                    'Test must be a subclass from Validator')
                raise

    def test_metaclass_1a(self):
        from configvalidator.configvalidator import CollectMetaclass

        class Test(object):
            pass
        self.assertEqual("object", CollectMetaclass.get_basis_name(Test()))

    def test_singleton(self):
        from configvalidator.configvalidator import StoreSingleton

        class A(object):
            name = "A"
        a = StoreSingleton()
        b = StoreSingleton()
        t = A()
        a.add_feature(t)
        self.assertEqual(a._instance, b._instance)
        self.assertEqual(t, b.get_feature("A"))

    def test_attributeDict_1(self):
        from configvalidator.configvalidator import AttributeDict
        a = AttributeDict()
        self.assertFalse("x" in a)

    def test_attributeDict_2(self):
        from configvalidator.configvalidator import AttributeDict
        a = AttributeDict({"x": 1})
        self.assertTrue("x" in a)
        self.assertEqual(a.x, 1)
        self.assertEqual(a["x"], 1)

    def test_attributeDict_3(self):
        from configvalidator.configvalidator import AttributeDict
        a = AttributeDict({"has_key": 1})
        self.assertTrue("has_key" in a)

    def test_attributeDict_4(self):
        from configvalidator.configvalidator import AttributeDict
        a = AttributeDict({"a": {"b": 1}})
        self.assertEquals(a.get("a", "b"), 1)

    def test_attributeDict_5(self):
        from configvalidator.configvalidator import AttributeDict
        a = AttributeDict()
        with self.assertRaises(AttributeError):
            a.x
            
    def test_externel_import_1a(self):
        with mock.patch.object(cv_to_mock.logger, 'error') as mock_method:
            c = {
                "Test": {
                    "t1": {
                        "feature": "EI2",
                    },
                }
            }
            imp.load_source("feature2", os.path.join(os.path.dirname(__file__), "feature2.py"))
            imp.load_source("feature2", os.path.join(os.path.dirname(__file__), "feature2.py"))
            conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
            self.assertEqual(1, len(conf))
            self.assertEqual(1, len(conf.Test))
            self.assertEqual("ABC", conf.Test.t1)
        mock_method.assert_called_once_with("maybe duplicate feature with name EI2")
        
    def test_externel_import_1b(self):
        with mock.patch.object(cv_to_mock.logger, 'error') as mock_method:
            c = {
                "Test": {
                    "t1": {
                        "default": "test",
                        "validator": "EV1",
                    },
                }
            }
            imp.load_source("validator", os.path.join(os.path.dirname(__file__), "validator.py"))
            imp.load_source("validator", os.path.join(os.path.dirname(__file__), "validator.py"))
            conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
            self.assertEqual(1, len(conf))
            self.assertEqual(1, len(conf.Test))
            self.assertEqual("test", conf.Test.t1)
        mock_method.assert_called_once_with("maybe duplicate validator with name EV1")
        
    def test_validator_port_a(self):
        c = {
                "Test": {
                    "t1": {
                        "default": "534",
                        "validator": "PORT",
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual(534, conf.Test.t1)
        
    def test_validator_port_b(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                "Test": {
                    "t1": {
                        "default": "0",
                        "validator": "PORT",
                    },
                }
            }
            ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "PORT" with input "0" return False for [Test]->t1')
        
    def test_validator_port_c(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                "Test": {
                    "t1": {
                        "default": "65536",
                        "validator": "PORT",
                    },
                }
            }
            ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "PORT" with input "65536" return False for [Test]->t1')
        
    def test_validator_port_d(self):
        c = {
                "Test": {
                    "t1": {
                        "default": "65535",
                        "validator": "PORT",
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual(65535, conf.Test.t1)
        
    def test_validator_url_a(self):
        c = {
                "Test": {
                    "t1": {
                        "default": "http://test.de",
                        "validator": "URL",
                        "URL_SCHEME": ["http", "https"],
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual('http://test.de', conf.Test.t1)
        
    def test_validator_url_b(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                "Test": {
                    "t1": {
                        "default": "http://test.de",
                        "validator": "URL",
                        "URL_SCHEME": ["https"],
                    },
                }
            }
            ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "URL" with input "http://test.de" return False for [Test]->t1')

    def test_validator_url_c(self):
        c = {
                "Test": {
                    "t1": {
                        "default": "ftp://test.de",
                        "validator": "URL",
                        "URL_SCHEME": None,
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual('ftp://test.de', conf.Test.t1)
        
    def test_validator_url_e(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                "Test": {
                    "t1": {
                        "default": "http://test.de",
                        "validator": "URL",
                    },
                }
            }
            ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "URL" required entry "URL_SCHEME" for [Test]->t1')

    def test_validator_float_a(self):
        c = {
                "Test": {
                    "t1": {
                        "default": "10.4",
                        "validator": "FLOAT",
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual(10.4, conf.Test.t1)
        
    def test_validator_float_b(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                "Test": {
                    "t1": {
                        "default": "fuuuubar",
                        "validator": "FLOAT",
                    },
                }
            }
            ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "FLOAT" with input "fuuuubar" return False for [Test]->t1')
        
    def test_validator_path_a(self):
        c = {
                "Test": {
                    "t1": {
                        "default": os.path.abspath(os.path.dirname(__file__)),
                        "validator": "PATH",
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual(os.path.abspath(os.path.dirname(__file__)), conf.Test.t1)
        
    def test_validator_path_b(self):
        _path = os.path.join(os.path.dirname(__file__), "tr348t893zhfjwh34zr4rhtre")
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                "Test": {
                    "t1": {
                        "default":  _path,
                        "validator": "PATH",
                    },
                }
            }
            ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "PATH" with input "' +_path+ '" return False for [Test]->t1')
        
        
    def test_validator_Number_a(self):
        c = {
                "Test": {
                    "t1": {
                        "default": "10.4",
                        "validator": "Number",
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual(10.4, conf.Test.t1)
        
    def test_validator_Number_b(self):
        c = {
                "Test": {
                    "t1": {
                        "default": "15",
                        "validator": "Number",
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual(15, conf.Test.t1)
  
    def test_validator_Number_c(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                "Test": {
                    "t1": {
                        "default": "fuuuubar",
                        "validator": "Number",
                    },
                }
            }
            ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "Number" with input "fuuuubar" return False for [Test]->t1')

    def test_validator_REGEX_a(self):
        c = {
                "Test": {
                    "t1": {
                        "default": "15",
                        "validator": "REGEX",
                        "REGEX_pattern": "^[0-9]{2}$"
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual("15", conf.Test.t1)
        
    def test_validator_REGEX_c(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                    "Test": {
                        "t1": {
                            "default": "153",
                            "validator": "REGEX",
                            "REGEX_pattern": "^[0-9]{2}$"
                        },
                    }
                }
            ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "REGEX" with input "153" return False for [Test]->t1')
        
    def test_validator_REGEX_d(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                    "Test": {
                        "t1": {
                            "default": "1dfds",
                            "validator": "REGEX",
                        },
                    }
                }
            ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "REGEX" required entry "REGEX_pattern" for [Test]->t1')
    
    def test_validator_REGEX_e(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                    "Test": {
                        "t1": {
                            "default": "ggg",
                            "validator": "REGEX",
                            "REGEX_pattern": None,
                        },
                    }
                }
            ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Can not compile regex "None" for [Test]->t1')
    
    
    def test_validator_IP4Validator_a(self):
        c = {
                "Test": {
                    "t1": {
                        "default": "254.0.0.1",
                        "validator": "IP4",
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual("254.0.0.1", conf.Test.t1)
        
    def test_validator_IP4Validator_b(self):
        c = {
                "Test": {
                    "t1": {
                        "default": "127.0.0.1",
                        "validator": "IP4",
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual("127.0.0.1", conf.Test.t1)
        
    def test_validator_IP4Validator_c(self):
        c = {
                "Test": {
                    "t1": {
                        "default": "255.255.255.255",
                        "validator": "IP4",
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual("255.255.255.255", conf.Test.t1)
        
    def test_validator_IP4Validator_e(self):
        c = {
                "Test": {
                    "t1": {
                        "default": "0.0.0.0",
                        "validator": "IP4",
                    },
                }
            }
        conf = ConfigValidator(
                ini_path=os.path.join(
                    base,
                    "1.ini"),
                ini_validator=c).parse()
        self.assertEqual(1, len(conf))
        self.assertEqual(1, len(conf.Test))
        self.assertEqual("0.0.0.0", conf.Test.t1)
        
    def test_validator_IP4Validator_f(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                    "Test": {
                        "t1": {
                            "default": "01.0.0.0",
                            "validator": "IP4",
                        },
                    }
                }
            ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "IP4" with input "01.0.0.0" return False for [Test]->t1')
    
    def test_validator_IP4Validator_g(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                    "Test": {
                        "t1": {
                            "default": "127.0",
                            "validator": "IP4",
                        },
                    }
                }
            ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "IP4" with input "127.0" return False for [Test]->t1')

    def test_validator_IP4Validator_h(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                    "Test": {
                        "t1": {
                            "default": "127.0.0.1.",
                            "validator": "IP4",
                        },
                    }
                }
            ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "IP4" with input "127.0.0.1." return False for [Test]->t1')
   
    def test_validator_IP4Validator_i(self):
        with self.assertRaises(ConfigValidatorException) as e:
            c = {
                    "Test": {
                        "t1": {
                            "default": "....",
                            "validator": "IP4",
                        },
                    }
                }
            ConfigValidator(
                    ini_path=os.path.join(
                        base,
                        "1.ini"),
                    ini_validator=c).parse()
        self.assertEqual(str(e.exception), 'Validator "IP4" with input "...." return False for [Test]->t1')

if __name__ == "__main__":
    unittest.main()
