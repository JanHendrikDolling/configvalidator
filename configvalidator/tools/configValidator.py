# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

import abc
import six
import json
import logging
from configvalidator.tools.basics import load_section_feature
from configvalidator.tools.parser import ParseObj
from configvalidator.tools.exceptions import InitException


logger = logging.getLogger(__name__)


class ConfigValidator(object):
    """ConfigValidator

    Attributes:
        cp: An class which fulfill the configparser interface
        cp_init_args: This item will be passed as kwargs to new cp instances
        data: local data store

    """

    def __init__(self, cp, cp_init_args=None):
        """Inits ConfigValidator."""
        self.cp = cp
        assert isinstance(cp, object)
        self.cp_init_args = cp_init_args
        assert isinstance(self.cp_init_args, dict) or self.cp_init_args is None
        self.data = {}
        for method_name in ["has_option", "read", "get", "options"]:
            if method_name not in dir(cp):
                raise InitException("No such method \"{method_name}\". Need to implement the ConfigParser interface".format(method_name=method_name))

    def add_data(self, key, value):
        """
	TODO
        """
        self.data[key] = value

    def remove_data(self, key):
        """
	TODO
        """
        assert isinstance(key, object)
        del self.data[key]

    def parse(self, config_dict, feature_key="__feature__"):
        """

        :param config_dict:
        :param feature_key:
        :return:
        """
        parse_obj = ParseObj(self.cp, cp_init_args=self.cp_init_args, context_data=dict(self.data))
        # copy config dict so that changes wont affect the original dict.
        tmp_config_dict = json.loads(json.dumps(config_dict))
        for section, section_config_dict in tmp_config_dict.items():
            try:
                parse_obj.current_section = section
                section_class_name = "default"
                if feature_key in section_config_dict:
                    section_class_name = section_config_dict[feature_key]
                    del section_config_dict[feature_key]
                section_class = load_section_feature(section_class_name)
                section_instance = section_class(parse_obj, **section_config_dict)
                section_instance.parse_section(parse_obj, section_config_dict)
            except Exception as e:
                parse_obj.add_error(error_msg="Error parsing section {section}: {raise_msg}".format(section=section, raise_msg=e), exception=e)
        parse_obj.current_section = None
        parse_obj.current_option = None
        return parse_obj.result()
