# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

import abc
import six
import json
import logging
from six import string_types
from collections import namedtuple
from configvalidator.tools.exceptions import LoadException, ValidatorException
from configvalidator.tools.parser import ParseObj


logger = logging.getLogger(__name__)

DATA_SECTION_FEATURE = {}
DATA_OPTION_FEATURE = {}
DATA_VALIDATOR = {}

GLOBAL_DATA = {}


def add_data(key, value):
    """Add a value to the global data store

    Validators and Features can access this data.
    If you create an object an *data* attribute is automatic added to the instance.
    This data attribute hold all information that there president during initialization.

    So it's possible to add additional meta data to Validators and Features.

    Args:
        key: The key under which that information is stored.
        value: The information

    """
    GLOBAL_DATA[key] = value


def remove_data(key):
    """remove a value from the global data store

    This removes the data only for new instances.
    The information remain available under the key for existing instances.

    Args:
        key: The key under which that information is stored.

    """
    del GLOBAL_DATA[key]


def load_validator(validator_name):
    """loads a validator class

    Args:
        validator_name: the validator name

    Returns:
        A validator class which than can be instanced

    Raises:
        KeyError: iff the validator_name is unknown
    """
    try:
        return DATA_VALIDATOR[validator_name]
    except KeyError:
        raise LoadException("no validator with the name {name}".format(name=validator_name))


def load_section_feature(feature_name):
    try:
        return DATA_SECTION_FEATURE[feature_name]
    except KeyError:
        raise LoadException(
            "no Section feature with the name {name}".format(name=feature_name))


def load_option_feature(feature_name):
    try:
        return DATA_OPTION_FEATURE[feature_name]
    except KeyError:
        raise LoadException(
            "no option feature with the name {name}".format(name=feature_name))


def load_validator_form_dict(option_dict):
    validator_class_name = "default"
    validator_class_dict = {}
    if isinstance(option_dict, dict) and "validator" in option_dict and option_dict["validator"] is not None:
        if isinstance(option_dict["validator"], string_types):
            validator_class_name = option_dict["validator"]
        else:
            validator_class_dict = option_dict["validator"]
            if "type" in validator_class_dict:
                validator_class_name = validator_class_dict["type"]
                del validator_class_dict["type"]
    return load_validator(validator_class_name), validator_class_dict


def list_objects():
    return dict(validators=[x for x in DATA_VALIDATOR],
                option_features=[x for x in DATA_OPTION_FEATURE],
                section_features=[x for x in DATA_SECTION_FEATURE])


def decorate_fn(func):
    def with_check_input_is_string(self, value):
        if not isinstance(value, string_types):
            raise ValidatorException("input must be a string.")
        return func(self, value)
    return with_check_input_is_string


class CollectMetaclass(abc.ABCMeta):

    """Metaclass which safes the class, so that the loads methods can find them.

    all classes with this metaclass are automatically collected

    The then can be accessed with there name (which is the class attribute
    name or the class name if the class has no attribute entry_name)
    """

    def __init__(self, name, bases, dct):
        """
        called then a new class is created.

        the method sets the "name" attribute if not set.
        if the attribute inactive is not False, the class
        is sort into the Singleton object
            - Validator to _env.validators
            - Feature to _env.features

        """
        super(CollectMetaclass, self).__init__(name, bases, dct)
        if object in bases:
            # skip base classes
            return
        if "name" not in dct:
            self.name = name
        if "inactive" not in dct or dct["inactive"] is not True:
            if issubclass(self, Validator):
                # only string input for validator functions
                self.validate = decorate_fn(self.validate)
                DATA_VALIDATOR[self.name] = self
            if issubclass(self, SectionFeature):
                DATA_SECTION_FEATURE[self.name] = self
            if issubclass(self, OptionFeature):
                DATA_OPTION_FEATURE[self.name] = self

    def __call__(self, *args, **kwargs):
        pars_obj = None
        if len(args) > 0 and isinstance(args[0], ParseObj):
            pars_obj = args[0]
            args = args[1:]
        res = self.__new__(self, *args, **kwargs)
        if isinstance(res, self):
            res.data = dict(GLOBAL_DATA)
            if pars_obj is not None:
                res.data.update(pars_obj.context_data)
            res.__init__(*args, **kwargs)
        return res


@six.add_metaclass(CollectMetaclass)
class Validator(object):

    """Superclass for Validator's

    If you want to write your own Validator use this Superclass.
    For Attribute information see Entry class.

    a instance lives in one section/option from ini_validator dict
    """

    @abc.abstractmethod
    def validate(self, value):
        """determine if one input satisfies this validator.

        IMPORTAND:
            The input is always are String

        Args:
            value (String): the value to check if it suffused this Validator

        Returns:
            True or False dependent of if the input suffused the Validator.
        """


@six.add_metaclass(CollectMetaclass)
class SectionFeature(object):

    def __init__(self, **kwargs):
        """
        :param kwargs: parameter will be ignored
        :return:
        """

    @abc.abstractmethod
    def parse_section(self, parse_obj, section_dict):
        """

        :param parse_obj: parser object which stores the data
        :param section_dict: the configuration dict for the current section
        :return:
        """


@six.add_metaclass(CollectMetaclass)
class OptionFeature(object):

    def __init__(self, **kwargs):
        """

        :param kwargs:  parameter will be ignored
        :return:
        """

    @abc.abstractmethod
    def parse_option(self, parse_obj, option_dict):
        """

        :param parse_obj: parser object which stores the data
        :param option_dict: the configuration dict for the current option
        :return:
        """
