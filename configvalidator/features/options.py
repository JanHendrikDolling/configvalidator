# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

import configvalidator
from configvalidator.tools.basics import load_validator_form_dict, load_validator, OptionFeature
from configvalidator.tools.exceptions import ParserException, ValidatorException
from configvalidator.tools.configValidator import ParseObj


def load():
    pass


class DefaultOptionFeature(OptionFeature):
    """
For a detailed explanation see chapter *The default option feature behavior is as followed*.

 * This feature has no required parameter.
 * This feature has the following optional parameter.
    * feature: To activate this feature parse the name "default" (string)
    * default: If not present, the entry is required. If present it holst the default value if no value is in the current ini file. (string)
    * validator: The validator configuration for the current option. (string or dict)
    * depends: Configuration to specify dependencies. (dict)
    """
    name = "default"

    def parse_option(self, parse_obj, option_dict):
        assert isinstance(parse_obj, ParseObj)
        assert isinstance(option_dict, dict)
        validator_class, validator_class_dict = load_validator_form_dict(option_dict)
        if "depends" in option_dict:
            dependencies = option_dict["depends"]
        else:
            dependencies = None
        if "default" in option_dict:
            default = option_dict["default"]
        else:
            default = None
        parse_obj.add_value(
            validator_class,
            validator_class_dict,
            dependencies_list=dependencies,
            default=default)


class SubIniOptionFeature(OptionFeature):
    """
This Feature checks if the value for the section/option entry is a valid file and then parse this file with the ConfigValidator module.
So the result for the section/option is the parse ini file, rather than the file path.

 * This feature has the following required parameter.
    * feature: to activate this feature parse the name "sub_ini" (string)
    * config: the configuration dict for the ConfigValidator module to parse the new ini file. (dict)
 * This feature has the following optional parameter.
    * feature_key: the dict key to search for features for sections. The default is "__feature__". (string)
    * default: if not present, the entry is required. If present it holst the default value if no value is in the current ini file. (string)

    remark: if the cp instance needs instantiate arguments (for the sub in a new instance is created), you can passe them to ConfigValidator constructor via cp_init_args dict.

    """
    name = "sub_ini"

    def __init__(self, config, feature_key="__feature__", default=None):
        super(SubIniOptionFeature, self).__init__()
        self._cv_config = config
        self._cv_feature_key = feature_key
        self._default = default
        self.parse_obj = None

    def parse_option(self, parse_obj, option_dict):
        self.parse_obj = parse_obj
        parse_obj.add_value(validator_class=load_validator("file"),
                            validator_init_dict={},
                            dependencies_list=None,
                            default=self._default,
                            custom_validate_fn=self._custom_validate_fn)

    def _custom_validate_fn(self, section, option, validator, raw_value):
        validator.validate(raw_value)
        cp_class = self.parse_obj.cp.__class__
        cp_instance = cp_class(**self.parse_obj.cp_init_args)
        cp_instance.read(raw_value)
        cv = configvalidator.ConfigValidator(cp=cp_instance)
        for k, v in self.parse_obj.context_data.items():
            cv.add_data(k, v)
        data = cv.parse(config_dict=self._cv_config, feature_key=self._cv_feature_key)
        self.parse_obj.add(section, option, data)
