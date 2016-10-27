# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

import logging
from configvalidator.tools.basics import load_option_feature, SectionFeature, load_validator_form_dict
from configvalidator.tools.exceptions import ParserException
from configvalidator.tools.configValidator import ParseObj
from six import string_types

logger = logging.getLogger(__name__)


def load():
    pass


class DefaultSectionFeature(SectionFeature):
    """
For a detailed explanation see chapter *The default section feature behavior is as followed*.

 * This feature has no required parameter.
 * This feature has the following optional parameter.
    * __feature__: to activate this feature parse the name "default" (string)

The return value that can be assessed in the result dict under the current section is also an result dict with the options as key.
    """
    name = "default"

    def parse_section(self, parse_obj, section_dict):
        assert isinstance(parse_obj, ParseObj)
        for option, option_config_dict in section_dict.items():
            parse_obj.current_option = option
            option_class_name = "default"
            if isinstance(option_config_dict, string_types):
                option_config_dict = {"validator": option_config_dict}
            else:
                if "feature" in option_config_dict:
                    option_class_name = option_config_dict["feature"]
                    del option_config_dict["feature"]
            option_class = load_option_feature(option_class_name)
            option_instance = option_class(parse_obj, **option_config_dict)
            option_instance.parse_option(parse_obj, option_config_dict)


class RawSectionInputFeature(SectionFeature):
    """
This Feature will parese a complete section with all contained options. 
So you don't have to declare every option in the dict, like you have to do in the default behavior.

 * This feature has the following required parameter.
    * __feature__: to activate this feature parse the name "rar_section_input" (string)
 * This feature has the following optional parameter.
    * validator: the validator configuration with is used to validate the options from this section. (string or dict) 
    * raise_error: if True the parsing process will fail if the validator fails for on option. If the value is False the option won't be in the result dict. default is True. (bool)
    * min: minimum required options that must be in the result dict. (int)
    * max: maximum required options that must be in the result dict. (ini)
    * depends: Configuration to specify dependencies. The structure ist the same as for *features for options* (dict)

The return value that can be assessed in the result dict under the current section is also an result dict with the options as key.
    """
    name = "raw_section_input"

    def __init__(
        self,
        validator=None,
        raise_error=True,
        min=None,
        max=None,
            depends=None):
        super(RawSectionInputFeature, self).__init__()
        validator_class, validator_class_dict = load_validator_form_dict(dict(validator=validator))
        self._validator_class = validator_class
        self._validator_class_dict = validator_class_dict
        self._raise_error = raise_error is True
        self._depends = depends
        self._parse_obj = None
        self._options_ok = None
        self._options_nok = None
        self._options_all = None
        self._min = min
        self._max = max

    def parse_section(self, parse_obj, section_dict):
        assert isinstance(parse_obj, ParseObj)
        self._parse_obj = parse_obj
        self._options_ok = []
        self._options_nok = []
        self._options_all = parse_obj.cp.options(parse_obj.current_section)
        for option in self._options_all:
            parse_obj.current_option = option
            parse_obj.add_value(validator_class=self._validator_class,
                                validator_init_dict=self._validator_class_dict,
                                dependencies_list=self._depends,
                                default=None,
                                custom_validate_fn=self._custom_validate_fn,
                                custom_error_fn=self._custom_error_fn)
        parse_obj.current_option = None

    def _custom_validate_fn(self, section, option, validator, raw_value):
        try:
            self._parse_obj.validate(
                section,
                option,
                validator,
                raw_value)
            self._options_ok.append(option)
        except Exception as e:
            if self._raise_error:
                raise ParserException("{option} - {error}".format(option=option, error=e))
            else:
                logger.debug("skip error in option [{section}]{option}: {msg}".format(section=section, option=option, msg=str(e)))
            self._options_nok.append(option)
        if len(self._options_ok) + len(self._options_nok) == len(self._options_all):
            # if the last option from this section is handled -> check if min
            # and max is okay
            if self._min is not None and self._min > len(self._options_ok):
                raise ParserException("minimum vailed options not reached")
            if self._max is not None and self._max < len(self._options_ok):
                raise ParserException("maximum vailed options reached")

    def _custom_error_fn(self, section, option, error):
        msg = "error validating [{section}]: {msg}".format(section=section,
                                                           option=option,
                                                           msg=error)
        logger.debug(msg)
        self._parse_obj.errors.append(msg)
