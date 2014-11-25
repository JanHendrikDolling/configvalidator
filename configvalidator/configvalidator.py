# -*- coding: utf-8 -*-
'''
Created on 22.03.2014

@license: http://www.apache.org/licenses/LICENSE-2.0
@author: Jan-Hendrik Dolling
'''
import os
import re
import json
import types
import logging
import inspect
import threading
from abc import ABCMeta
from abc import abstractmethod

import six
from six.moves import configparser
from six.moves.urllib.parse import urlparse


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logger = logging.getLogger("configvalidator")
logger.addHandler(NullHandler())


class StoreSingleton(object):

    """A Singelton to Store the known Entry's (Validator/ Feature)

    Attributes:
        _instance (Singleton): the attribute with stores the Singelton instance
    """
    _instance = None

    class Singleton(object):

        """The Singleton

        to get the Singleton instanz call Singleton().instance()
        with always return the same instance.

        Attributes:
           _singleton_lock (Lock): lock to ensure thread safety
                                   (class attribute)
           _singleton_instance (Singleton): the instance (class attribute)
           _features (Dict): stores the known features
           _validators (Dict): stores the known validators
        """
        _singleton_lock = threading.Lock()
        _singleton_instance = None

        def __init__(self):
            self._features = {}
            self._validators = {}
            self._elements = {}
            self._elements["feature"] = {}
            self._elements["validator"] = {}

        @classmethod
        def instance(cls):
            if not cls._singleton_instance:
                with cls._singleton_lock:
                    if not cls._singleton_instance:
                        cls._singleton_instance = cls()
            return cls._singleton_instance

    def __init__(self):
        """Inits StoreSingleton

        By instance the attribute with the Singleton instance
        """
        if not StoreSingleton._instance:
            StoreSingleton._instance = StoreSingleton.Singleton().instance()
        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = StoreSingleton._instance

    def add_validator(self, validator):
        """add a validator to the list of known validators

        Args:
            validator: the validator to add
        """
        self._instance._validators[validator.name] = validator

    def add_feature(self, feature):
        """add a feature to the list of known features

        Args:
            feature: the feature to add
        """
        self._instance._features[feature.name] = feature

    def get_feature(self, feature_name):
        """returns the feature class definition by feature name

        Args:
            feature_name (String): the name of the feature to return

        Returns:
            the feature class if a class with this name was define
        """
        return self._instance._features[feature_name]

    def get_validator(self, entry_name):
        """returns the validator class definition by validator name

        Args:
            entry_name (String): the name of the validator to return

        Returns:
            the validator class if a class with this name was define
        """
        return self._instance._validators[entry_name]

    def has_feature(self, feature_name):
        """returns True if the feature class with the given name was define

        Args:
            feature_name (String): the name of the feature

        Returns:
            True if this feature was define
        """
        return feature_name in self._instance._features

    def has_validator(self, entry_name):
        """returns True if the validator class with the given name was define

        Args:
            entry_name (String): the name of the feature

        Returns:
            True if this validator was define
        """
        return entry_name in self._instance._validators

    def add_entry(self, entry_type, entry, name, bases, dct):
        """add new Feature or Validator class to the list of known class's

         Args:
             entry_type (string): feature or validator
             entry: the class
             (name, bases, dct): class definition from the metaclass

         Raises:
             ConfigValidatorException: if the class is already define
        """
        has_fn = getattr(self, "has_{0}".format(entry_type))
        add_fn = getattr(self, "add_{0}".format(entry_type))
        if not has_fn(entry.name):
            add_fn(entry)
            self._instance._elements[entry_type][
                entry.name] = (name, bases, dct)
        else:
            (name_pres, bases_pres, dct_pres) = self._instance._elements[
                entry_type][entry.name]
            if name == name_pres:
                def _different():
                    if len(bases) != len(bases_pres):
                        return True
                    for item in bases:
                        if item not in bases_pres:
                            return True
                    if dct.keys() != dct_pres.keys():
                        return True
                    for key, value in dct.items():
                        if key == "__module__":
                            continue
                        try:
                            if inspect.getargspec(value) != \
                               inspect.getargspec(dct_pres[key]):
                                return True
                        except TypeError:
                            if value != dct_pres[key]:
                                return True
                    return False
                if not _different():
                    logger.error("maybe duplicate {0} with\
 name {1}".format(entry_type, entry.name))
                    return
            raise ConfigValidatorException("duplicate {0} \
name {1}".format(entry_type, entry.name))


class CollectMetaclass(ABCMeta):

    """Metaclass wich safes the class in the _env module variable

    all Subclasses of Entry (Validator/ Feature) are automaticly collect
    and stored in the Singleton object.

    The then can be acced with ther name (wich is the class attribute
    name or the class name if the class has no
    attribute entry_name)
    """

    def __init__(self, name, bases, dct):
        """
        called then a new class from type Entry (Validator/ Feature) is
        createt.

        the method sets the "name" attribute if not set.
        it the attribute inaktiv is not set False,
        the class is sort intor the Singleton object
            - Validator to _env.validators
            - Feature to _env.features

        """
        super(CollectMetaclass, self).__init__(name, bases, dct)
        if "name" not in dct:
            self.name = name
        if "inaktiv" not in dct or not dct["inaktiv"]:
            store = StoreSingleton()
            if CollectMetaclass.is_Validator(bases):
                store.add_entry("validator", self, name, bases, dct)
            if CollectMetaclass.is_Feature(bases):
                store.add_entry("feature", self, name, bases, dct)

    @classmethod
    def is_Validator(cls, parents):
        """helper method to check if this is a subclass of Validator

        Args:
            parents (class list): list with classes to check

        Returns:
            True if on of the class is of instance Validator
        """
        return cls._rec_call(CollectMetaclass.__module__ + ".Validator",
                             parents, lambda x: cls.is_Validator(x))

    @classmethod
    def is_Feature(cls, parents):
        """helper method to check if this is a subclass of Feature

        Args:
            parents (class list): list with classes to check

        Returns:
            True if on of the class is of instance Feature
        """
        return cls._rec_call(CollectMetaclass.__module__ + ".Feature",
                             parents, lambda x: cls.is_Feature(x))

    @classmethod
    def _rec_call(cls, name, object_list, fn):
        for item in object_list:
            if item.__module__ + "." + item.__name__ == name:
                return True
            if fn(item.__bases__):
                return True
        return False

    @classmethod
    def get_basis_name(cls, instance):
        """get the suberclass name of this instance

        Args:
            instance: a object instance

        Returns:
            name of the superclass - on of
                - Validator/Feature
                - Feature
                - Validator
                - Entry
        """
        f = cls.is_Feature(instance.__class__.__bases__)
        v = cls.is_Validator(instance.__class__.__bases__)
        if f and v:
            return "Validator/Feature"
        if f:
            return "Feature"
        if v:
            return "Validator"
        return "object"


@six.add_metaclass(CollectMetaclass)
class Entry(object):

    """Superclass for Validator and Features

    Add metaclass functionality to Validator and Features classes.
    Add the basic attributes to Validator and Features classes.

    IMPORTAND:
    if you write your own subclass from Validator and Features and
    you create your own __init__ methode don't forget to call
    super(self.__class__, self).__init__()

    The folloring class attributes are possible:
        name (String): The globale name for this Validator/Features
                       under which it can be used in the ini_validator dict.
        inaktiv (bool): if set to True this class can't be used in
                        the ini_validator dict.

    Attributes:
        enviroment: referent to the enviroment object.
        section (String): the section there the instance lifes.
        option (String): the option there the instance lifes.
    """
    name = None
    inaktiv = False

    def __init__(self):
        """Inits Entry

        Raises:
            ConfigValidatorException: if enviroment is not pressent or None
        """
        super(Entry, self).__init__()
        if (not hasattr(self, "enviroment") or
                not self.enviroment or
                not isinstance(self.enviroment, ConfigValidator.Environment)):
            raise ConfigValidatorException(
                "instance error - create instance via \
enviroment get_instance method")

    def __new__(cls, enviroment=None):
        """create new instances

        Args:
            cls (class): the class to create a instance form
            enviroment (Enviroment): the Enviroment for this instance

        Returns:
            a new instance - you should call __init__ ather this

        Raises:
           ConfigValidatorException: -if no enviroment is passed
                                     -if not all required entry in
                                      this section/option
        """
        inst = super(Entry, cls).__new__(cls)
        inst.enviroment = enviroment
        if enviroment and isinstance(enviroment, ConfigValidator.Environment):
            inst.section = enviroment.get_current_section()
            inst.option = enviroment.get_current_option()
            for item in cls.required_records():
                if item not in inst._get_dict().keys():
                    raise ConfigValidatorException(
                        "{4} \"{2}\" required entry \"{3}\" for [{0}]->{1}".
                        format(inst.section, inst.option, cls.name,
                               item, CollectMetaclass.get_basis_name(inst)))
        else:
            Entry.__init__(inst)
        return inst

    def _get_dict(self):
        """ini_validator dict from section/option

        Returns:
            The dict for the section/option from this Object.
        """
        return self.enviroment.ini_validator[self.section][self.option]

    @classmethod
    def required_records(cls):
        """Return's List with required ini_validator dict entry's

        This is a static class method and vailed for all instances.
        Overrride in subclasses if your Validator/Feature has requrements.

        Returns:
            list with required elements

            if ["foo"] is returned an this Validator/Features is vaild in the
            section/option. e.g. A/B then the ini_validator dict looks like
            (summary)
            "A": {
                "B": {
                    "foo": somthing,
                },
            },
        """
        return []


class Validator(Entry):

    """Superclass for Validator's

    If you want to write your own Validator use this Superclass.
    For Attribute information see Entry class.

    a instance lifes in one section/option from ini_validator dict
    """

    @abstractmethod
    def validate(self, value):
        """determine if one input satisfies this validator.

        IMPORTAND:
            The input is always are String

        Args:
            value (String): the value to check if it suffused this Validator

        Returns:
            True or False dependent of if the input suffused the Validator.
        """

    @abstractmethod
    def transform(self, value):
        """transform the type

        IMPORTAND:
            The input is always are String

        Args:
            value (String): the value to transform

        Returns:
            the type of value maybe changes
        """


class TrueValidator(Validator):

    """Validator there all import are permitted

    This Validator can be addressed with: TRUE
    """
    name = "TRUE"

    def validate(self, value):
        """determine if one input satisfies this validator.

        call the transform method and return True if no Exception occure.

        Args:
            value (String): the value to check if it suffused this Validator

        Returns:
            True or False dependent of if the input suffused the Validator.
        """
        try:
            self.transform(value)
            return True
        except:
            return False

    def transform(self, value):
        """identity

        Args:
            value (String): the value to transform

        Returns:
            the value unchanged
        """
        return value


class ReturnValidator(TrueValidator):

    """internal Validator with wrapps the function from the "return" entry
    in the ini_validator dict.

    Attributes:
        _return (Function): the function with transform the value
        name (String): if an exception occures this name is displayed
        inaktiv (bool): this validator can't acces in the ini_validator dict
    """
    inaktiv = True

    def __init__(self, _return):
        super(ReturnValidator, self).__init__()
        self._return = _return
        self.name = "ReturnValidator(" + self._return.__name__ + ")"

    def transform(self, value):
        return self._return(value)


class IntValidator(TrueValidator):
    name = "INT"

    def transform(self, value):
        return int(value)


class BoolValidator(TrueValidator):
    name = "BOOL"

    def transform(self, value):
        return value.lower() in ("yes", "true", "t", "1")


class JsonValidator(TrueValidator):
    name = "JSON"

    def transform(self, value):
        return json.loads(value)


class StringValidator(TrueValidator):
    name = "STRING"

    def validate(self, value):
        return isinstance(value, six.string_types)


class OrValidator(TrueValidator):

    """Validator with are list of Validator's - to bee True
    one of them must be True

    Attributes:
        validators (List): List of validators to check
    """
    name = "OR"

    def __init__(self):
        """Inits OrValidator

        evalutest the entry "validator_OR" from the ini_validator dict.
        This entry contains a list with Validator names.
        This validators are loaded.

        Raises:
            ConfigValidatorException: if a Validator from "validator_OR"
                                      can't bee instanced
        """
        super(OrValidator, self).__init__()
        self.validators = []
        self._uses_validator = None
        for validator in self._get_dict()["validator_OR"]:
            try:
                self.validators.append(
                    self.enviroment.get_instance(
                        self.enviroment.load_validator(validator)))
            except:
                raise ConfigValidatorException(
                    "validator_OR: can not instance Validator \"{2}\" \
[no method __init__(self)] for [{0}]->{1}".
                    format(self.section, self.option, validator))

    @classmethod
    def required_records(cls):
        return ["validator_OR"]

    def validate(self, value):
        """validate function form OrValidator

        Returns:
            True if at least one of the validators
            validate function return True
        """
        for val in self.validators:
            if val.validate(value):
                self._uses_validator = val
                return True
        return False

    def transform(self, value):
        if self._uses_validator is None:
            return value
        return self._uses_validator.transform(value)


class FileValidator(TrueValidator):
    name = "FILE"

    def validate(self, value):
        return value and os.path.exists(value) and os.path.isfile(value)


class EmailValidator(TrueValidator):
    name = "EMAIL"

    def __init__(self):
        super(self.__class__, self).__init__()
        EMAIL_method = {
            "regex": self._validate_regex,
            "parseaddr": self._validate_parseaddr,
        }
        if "EMAIL_method" in self._get_dict():
            method = self._get_dict()["EMAIL_method"]
        else:
            method = "regex"
        if method in EMAIL_method:
            self._validate = EMAIL_method[method]
        else:
            raise ConfigValidatorException("no Email Validator method \"{0}\" \
for [{1}]->{2}".format(method, self.section, self.option))

    def validate(self, value):
        return self._validate(value)

    def _validate_regex(self, value):
        return re.match(r"[^@]+@[^@]+\.[^@]+", value)

    def _validate_parseaddr(self, value):
        from email.utils import parseaddr
        return parseaddr(value)[1] != ''


class PortValidator(IntValidator):
    name = "PORT"

    def validate(self, value):
        return super(self.__class__, self).validate(value) \
            and int(value) >= 1 \
            and int(value) <= 65535


class URLValidator(TrueValidator):
    name = "URL"

    def __init__(self):
        super(self.__class__, self).__init__()
        self._url_scheme = []
        self._wildcard = self._get_dict()["URL_SCHEME"] is None
        if not self._wildcard:
            for scheme in self._get_dict()["URL_SCHEME"]:
                self._url_scheme.append(scheme.lower())

    @classmethod
    def required_records(cls):
        return ["URL_SCHEME"]

    def validate(self, value):
        try:
            o = urlparse(value)
            if self._wildcard:
                return True
            if o.scheme.lower() in self._url_scheme:
                return True
        except:
            pass
        return False


class FloatValidator(TrueValidator):
    name = "FLOAT"

    def transform(self, value):
        return float(value)


class PathValidator(TrueValidator):
    name = "PATH"

    def validate(self, value):
        return value and os.path.exists(value) and os.path.isdir(value)


class NumberValidator(OrValidator):
    name = "Number"

    def __init__(self):
        super(Validator, self).__init__()
        self.validators = []
        self.validators.append(
            self.enviroment.get_instance(
                self.enviroment.load_validator("INT")))
        self.validators.append(
            self.enviroment.get_instance(
                self.enviroment.load_validator("FLOAT")))

    @classmethod
    def required_records(cls):
        return []


class RegexValidator(TrueValidator):
    name = "REGEX"

    def __init__(self):
        super(self.__class__, self).__init__()
        regex = None
        try:
            regex = self._get_dict()["REGEX_pattern"]
            self._pattern = re.compile(regex)
        except:
            raise ConfigValidatorException("Can not compile regex \"{0}\" \
for [{1}]->{2}".format(regex, self.section, self.option))

    @classmethod
    def required_records(cls):
        return ["REGEX_pattern"]

    def validate(self, value):
        try:
            return self._pattern.match(value) is not None
        except:
            return False


class IP4Validator(TrueValidator):
    name = "IP4"

    def __init__(self):
        super(self.__class__, self).__init__()

    def validate(self, value):
        try:
            res = value.split(".")
            if len(res) == 4:
                for item in res:
                    if not 0 <= int(item) < 256:
                        return False
                    if len(item) > 1 and item[0] == "0":  # no leading zero's
                        return False
                return True
        except:
            pass
        return False


class Feature(Entry):

    """Superclass for Feature's

    If you want to write your own Feature use this Superclass.
    For Attribute information see Entry class.

    a instance lifes in one section/option from ini_validator dict
    """

    @abstractmethod
    def execute(self):
        """run the Feature

        implementation of the Feature.
        This method is called ones and returen the result.
        The result is later retrievable via section/option

        Returns:
            The value for this section/option
        """


class DefaultFeature(Feature):

    """Default Feature with is uses if no Feature is given

    This Feature is inactiv and can't bee used from outside.

    Attributes:
        validator (Validator): the validator for this section/option
    """
    inaktiv = True

    def __init__(self, validator):
        super(DefaultFeature, self).__init__()
        self.validator = validator

    def execute(self):
        """run this Feature

        get the value from the ini file or the default value.
        then checks if the value is vaildat for the given validator.

        if the section "transform" is in the ini_validator dict and the
        the value is False then the result will re returned as String overwise
        the transform method from the validator will be used to change the
        return type.

        Raises:
            ConfigValidatorException: -if no default section and no value in
                                       the ini file
                                      -if the validator validate method
                                       return False
        """
        if self.enviroment.config.has_option(self.section, self.option):
            value = self.enviroment.config.get(self.section, self.option)
        else:
            if "default" in self._get_dict():
                value = self._get_dict()["default"]
            else:
                raise ConfigValidatorException("[{0}][{1}] not in ini file".
                                               format(self.section,
                                                      self.option))
        if not self.validator.validate(value):
            raise ConfigValidatorException(
                "Validator \"{0}\" with input \"{1}\" return False for \
[{2}]->{3}".format(self.validator.name, value, self.section,
                   self.option))
        if ("transform" in self._get_dict() and
                not self._get_dict()["transform"]):
            return value
        return self.validator.transform(value)


class ListFeature(Feature):

    """Return a List

    This Feature can be used by the term "LIST_INPUT"

    in the ini file this Feature can be actived by setting the section/option
    to True

    if the section/option ist True then all elements from the section from the
    ini file
    with is given via "LIST_INPUT_section" is transformed to da dict. There the
    key a the
    option names and the values a the values form the ini file.

    the valures will be validated via the "LIST_INPUT_validator" or
    "LIST_INPUT_return" variable

    if "LIST_INPUT_exit_on_error" is set to true all values musst be secsessful
    transformed.

    Attributes:
        validator (Validator): the validator for the values from the
                               "LIST_INPUT_section"
        aktive (DefaultFeature): checks if the ListFeature is aktiv or not
        LIST_INPUT_exit_on_error (Bool): if True all values from the
                                         "LIST_INPUT_section" must calidate
                                          via validator
        LIST_INPUT_section (String): The name of the section this is used from
                                     the ini file for the ListFeature

    Raises:
        ConfigValidatorException: if the validator can't instance
    """
    name = "LIST_INPUT"

    def __init__(self):
        super(ListFeature, self).__init__()
        self.validator = self.enviroment.get_validator(prefix="LIST_INPUT_")
        self.aktive = self.enviroment.get_instance(
            DefaultFeature,
            self.enviroment.get_instance(BoolValidator))
        self.LIST_INPUT_exit_on_error = self._get_dict(
        )["LIST_INPUT_exit_on_error"]
        self.LIST_INPUT_section = self._get_dict()["LIST_INPUT_section"]

    @classmethod
    def required_records(cls):
        """the required_records

        The required_records "LIST_INPUT_return" or "LIST_INPUT_validator"
        are implicitly requred via Attribute validator

        Returns:
            List with required_records
        """
        return ["LIST_INPUT_section", "LIST_INPUT_exit_on_error"]

    def execute(self):
        """run the feature

        Returns:
            None if the Featur is not activ - Dict otherwise

        Raises:
            ConfigValidatorException: if not all values can the validate or a
                                      Exception occures
        """
        if self.aktive.execute():
            res = {}
            if self.enviroment.config.has_section(self.LIST_INPUT_section):
                for (name, val) in (self.enviroment.config.items(
                        self.LIST_INPUT_section)):
                    try:
                        if self.validator.validate(val):
                            res[name] = self.validator.transform(val)
                        elif self.LIST_INPUT_exit_on_error:
                            raise ConfigValidatorException(
                                "[{0}][{1}] validation error at index \
\"{2}\" with input \"{3}\"".format(self.section, self.option, name, val))
                    except ConfigValidatorException as e:
                        raise e
                    except Exception as e:
                        if self.LIST_INPUT_exit_on_error:
                            raise ConfigValidatorException("[{0}][{1}] \
Exception at {2} | msg: {3}".format(self.section, self.option, name, e))
            else:
                if self.LIST_INPUT_exit_on_error:
                    raise ConfigValidatorException("No Section: \
{0}".format(self.LIST_INPUT_section))
            return res
        else:
            return None


class SubIniFeature(Feature):

    """Sub INI Feature

    The value is an Filepath to another ini
    The ini will then Validate via the config form "SUB_INI_config"

    If None is passed the ini File ist not evalueded

    Attributes:
       aktive (Feature): check if the feature ist aktive
       validator (Validator): a Validator to check the result of the feature
       config (Dict): the ini_validator dict for the ini
    """
    name = "SUB_INI"

    def __init__(self):
        super(SubIniFeature, self).__init__()
        self.aktive = self.enviroment.get_instance(
            DefaultFeature,
            self.enviroment.get_instance(TrueValidator))
        self.validator = self.enviroment.get_instance(FileValidator)
        self.config = self._get_dict()["SUB_INI_config"]

    @classmethod
    def required_records(cls):
        return ["SUB_INI_config"]

    def execute(self):
        ini_path = self.aktive.execute()
        if not ini_path or ini_path == "":
            return None
        if not os.path.isabs(ini_path):
            ini_path = os.path.abspath(os.path.join(os.path.dirname(
                self.enviroment.get_ini_path()), ini_path))
        try:
            return ConfigValidator(ini_path=ini_path,
                                   ini_validator=self.config).parse()
        except ConfigValidatorException as e:
            raise ConfigValidatorException("SUB_INI for [{0}]->{1} | msg: \
{2}".format(self.section, self.option, e))


class ConfigValidatorException(Exception):

    """
    This Exception is raised if somthing went wrong
    """
    pass


class ConfigValidator(object):

    """with this class you can verifie a ini file

    This class gets a ini file name ans an configuration dict. Then the ini
    file will be paresd and if no Exception occures you have a dict (which can
    bee accec via section/option) with the verified ini values.

    The ini file is a String to the ini file wich can be pasred with a
    ConfigParser.

    The ini_validator Dict has the follwoing form:
     - In the dict there is a section for every ini section
     - in each ini section ther is a entry for each option in this ini
       file section
     - each section/option is a dict with the following form:
        - if the key "feature" exist, the value referenz to a Feature class.
          What further entries are required depends on this Feture.
          New Feature can be ceated if your subclass the Feature class.
        - if no key "feature" exist:
          - if the key "result" exist.
            The value must be a function
          - if the key "validator" exist. The value referenz to a Validator
            class.
            What further entries are required depends on this Validator.
            New Validator's can be ceated if your subclass the Validator class.
          - if neither "result" nor "validator" key exists an exception is
             raised.
          - if the value "default" exist this value is used if no entrie for
            this section/option is present in the ini file.
            if "default" don't exist and no value for this section/option is
            in the ini file an exception is raised.
          - if the value "transform" exist and is set to False the method
            transform from the validator will not be called and the result type
            is from type String.

        This is an exampte of an ini_validator Dict:
            ini_validator = {
                "section_name_1":
                     "option_name_1": {
                         "validator": "TRUE",
                         "default": "None",
                         ...
                     },
                     "option_name_1": {
                         ...
                     },
                "section_name_2": {
                      ...
                },
            }

        Afther validation the result dict holdt an entry for each
        section/option in the ini_validator dict. even if the ini file has more
        or less entries.

        For each entry wich is not present in the ini file where must be a
        "default" entry under this section/option or the Feture class must
        hand whis correct.

        Every section/option in the ini file which is noch present in the
        ini_validator dict is ignored.

    Attributes:
        ini_validator (Dict): the ini_validator dict with the config
                              for this ConfigValidator instance
        _data (Dict): holds the result per section/option
        ini_path (filepath String): path to the ini file
        env (Environment): referenz to the Environment object
    """
    class Environment(object):

        """Environment object for the ConfigValidator

        This object holst helper methods to load Validators and Features

        Attributes:
            config (configparser): the ini object
            ini_validator (Dict): the ini_validator dict with the config for
                                  this ConfigValidator instance
            ini_path (path): the file path to the ini file
            section (string): the current section
            option (string): the current option
        """

        def __init__(self, configValidator_instance):
            """Inits Environment.

            Args:
                configValidator_instance (ConfigValidator): the ConfigValidator
                                                            instance referenz
            """
            self.ini_validator = configValidator_instance.ini_validator
            self.ini_path = configValidator_instance.ini_path
            self.config = configparser.RawConfigParser()
            self.config.read(self.ini_path)
            self.section = None
            self.option = None

        def get_ini_path(self):
            """
            Returns: the file path to the ini file
            """
            return self.ini_path

        def get_current_section(self):
            """
            Returns: the current section in the parsing process
            """
            return self.section

        def get_current_option(self):
            """
            Returns: the current option in the parsing process
            """
            return self.option

        def get_feature(self):
            """
            creates a Feature instance out of the current section/option

            Returns:
                the Feature instance

            Raises:
                ConfigValidatorException: -if no feture with this name (name
                                           from the current section/option)
                                           exist
                                          -if the feature is no subclass form
                                           Feature
            """
            section_option_dict = self.ini_validator[self.section][self.option]
            if "feature" in section_option_dict:
                feature = section_option_dict["feature"]
            else:
                return self.get_instance(DefaultFeature, self.get_validator())
            if isinstance(feature, six.string_types):
                store = StoreSingleton()
                if store.has_feature(feature):
                    feature = store.get_feature(feature)
                else:
                    raise ConfigValidatorException("No Feature with name {0} \
for [{1}]->{2}".format(feature, self.section, self.option))
            if not issubclass(feature, Feature):
                raise ConfigValidatorException("{0} must be a subclass from \
Feature".format(feature.__name__))
            return self.get_instance(feature)

        def get_validator(self, prefix=""):
            """
            creats a validator instance out of the current section/option
            prefix+"return" wins if it ist present

            Args:
                prefix (String): prefix+"validator" and prefix+"return" are
                                 used to geht the validator

            Returns:
                the Validator instance

            Raises:
                ConfigValidatorException: -if prefix+"validator" nore
                                           prefix+"return" is present
                                          -if prefix+"return" is no Function
            """
            section_option_dict = self.ini_validator[self.section][self.option]
            if (not (prefix + "validator" in section_option_dict or
                     prefix + "return" in section_option_dict)):
                raise ConfigValidatorException("\"{2}validator\" or \
\"{2}return\" required for [{0}]->{1}".format(self.section,
                                              self.option, prefix))
            if prefix + "return" in section_option_dict:
                _return = section_option_dict[prefix + "return"]
                if not isinstance(_return, types.FunctionType):
                    raise ConfigValidatorException("\"{2}return\" for \
[{0}]->{1} must be a Function".format(self.section, self.option, prefix))
                return self.get_instance(ReturnValidator, _return)
            else:
                validator = (self.load_validator(
                             section_option_dict[prefix + "validator"]))
                return self.get_instance(validator)

        def load_validator(self, entry_name):
            """
            return the validator class

            Args:
                entry_name (String): the name of the validator class

            Returns:
                the validator class

            Raises:
                ConfigValidatorException: if name not present
                                          if Class is no Subclass of Validator
            """
            if isinstance(entry_name, six.string_types):
                store = StoreSingleton()
                if store.has_validator(entry_name):
                    entry_name = store.get_validator(entry_name)
                else:
                    raise ConfigValidatorException("No Validator with name \
{0} for [{1}]->{2}".format(entry_name, self.section, self.option))
            if not issubclass(entry_name, Validator):
                raise ConfigValidatorException("{0} must be a subclass from \
Validator".format(entry_name.__name__))
            return entry_name

        def get_instance(self, entry_class, *init_args):
            inst = entry_class.__new__(entry_class, self)
            inst.__init__(*init_args)
            return inst

    def __init__(self, ini_path, ini_validator={}):
        """Inits ConfigValidator

        Args:
            ini_path (Filepath String): the path to the ini File
            ini_validator (Dict): the ini_validator dict with the validaton
                                  config

        Raises:
            ConfigValidatorException: if arg ini_validator is no dict
                                      if arg ini_path is no File or don't exist
        """
        if not isinstance(ini_validator, dict):
            raise ConfigValidatorException("parameter ini_validator must be \
a dict")
        if not os.path.exists(ini_path) or not os.path.isfile(ini_path):
            raise ConfigValidatorException("no file @ {0}".format(ini_path))
        self.ini_validator = ini_validator
        self._data = {}
        self.ini_path = ini_path
        self.env = ConfigValidator.Environment(self)

    def parse(self):
        """parse the ini file with the help of the ini_validator dict config

        Returns:
            An Object with the values accessible via section/option

            if the variable name ist "res" an section "x" with option "y"
            exist, you can enter the value via:
                - res.x.y
                - res["x"]["y"]
                - res.get("x", "y")

            The result object is immutable!

        Raises:
            ConfigValidatorException: if validation fails
        """
        for section_key in self.ini_validator:
            self._data[section_key] = {}
            for option_key in self.ini_validator[section_key]:
                self.env.section = section_key
                self.env.option = option_key
                feature = self.env.get_feature()
                self._data[section_key][option_key] = feature.execute()
        return AttributeDict(self._data)


class AttributeDict(dict):

    """
    Dict which holds the result values
    """

    def __getattr__(self, name):
        if name in self:
            val = self[name]
            if isinstance(val, AttributeDict):
                return AttributeDict(val)
            elif isinstance(val, dict):
                return AttributeDict(val)
            else:
                return val
        raise AttributeError(name)

    def get(self, section, option):
        return self[section][option]
