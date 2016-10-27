# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""
import logging
from collections import namedtuple
from configvalidator.tools.exceptions import ParserException
from configvalidator.tools.result import AttributeDict
from six import string_types


logger = logging.getLogger(__name__)
IniKey = namedtuple("IniKey", ["section", "option"])


class ParseObj(object):

    def __init__(self, cp, cp_init_args=None, context_data=None):
        self.cp = cp
        self.cp_init_args = cp_init_args
        if self.cp_init_args is None:
            self.cp_init_args = {}
        self.context_data = context_data
        if self.context_data is None:
            self.context_data = {}
        assert isinstance(self.context_data, dict)
        self.current_section = None
        self.current_option = None
        self.parsed_values = {}
        self.future_values_key_item = {}
        self.future_values_key_dep = {}
        self.errors = []

    def result(self):
        assert self.current_section is None
        assert self.current_option is None
        errors = list(self.errors)
        if self.future_values_key_item or self.future_values_key_dep:
            res = []
            for dep in self.future_values_key_item:
                res.append(
                    "'{section}'/'{option}'".format(
                        section=dep.section,
                        option=dep.option))
            errors.append("not all dependencies resolved: {res}".format(res="|".join(res)))
        if len(errors) > 0:
            raise ParserException("\n".join(errors))
        return AttributeDict(self.parsed_values)

    def add_value(
        self,
        validator_class,
        validator_init_dict,
        dependencies_list=None,
        default=None,
        custom_validate_fn=None,
            custom_error_fn=None):
        # posebility to set cudtiom validate methods for one section/option
        # if it can be validated (dependencies resolved)
        if custom_validate_fn is None:
            custom_validate_fn = self.validate
        if custom_error_fn is None:
            custom_error_fn = self._handle_error
        # read value or check if default value should bee used
        if not self.cp.has_option(self.current_section, self.current_option):
            if default is None:
                self.add_error("No value for Section/Option: '{section}'/'{option}'".format(section=self.current_section, option=self.current_option))
                return
            else:
                raw_value = default
        else:
            raw_value = self.cp.get(self.current_section, self.current_option)
        # check dependencies
        if dependencies_list is None:
            dependencies_list = []
        need_work = {}
        for dependencies_parameter in dependencies_list:
            dep_section, dep_option = validator_init_dict[dependencies_parameter]
            if self.has_option(dep_section, dep_option):
                # this dependencie can resolved instancly
                validator_init_dict[dependencies_parameter] = self.get(dep_section, dep_option)
            else:
                # this dependencie need to be resolved later. mayby at the end
                # of the parsing process
                need_work[dependencies_parameter] = (dep_section, dep_option)
        # check if future work is needed
        cur_key = IniKey(section=self.current_section, option=self.current_option)
        if not need_work:
            # all dependenvies where resolves, so this entry can be validated
            # instancly
            try:
                validator = self._get_validator(validator_class, validator_init_dict)
            except Exception as e:
                self._handle_error(section=self.current_section, option=self.current_option, error=str(e))
                return
            try:
                custom_validate_fn(self.current_section, self.current_option, validator, raw_value)
                self._resolve_dep(cur_key)
            except Exception as e:
                custom_error_fn(section=self.current_section, option=self.current_option, error=e)
        else:
            # check for syntax error in the depends dict
            for k, v in need_work.items():
                if (not isinstance(k, string_types) or not isinstance(v, tuple) or not len(v) == 2 or not len([x for x in v if isinstance(x, string_types)]) == 2):
                    self.add_error("error validating [{section}]{option}: depends syntax: 'str: (str, str)'".format(section=self.current_section, option=self.current_option))
                    return
            # generate dependencies dict
            gen_depend_dict = {}
            for k, (s, o) in need_work.items():
                gen_depend_dict[k] = IniKey(section=s, option=o)
            # add an future to calculate this entry, if the needed dependencies
            # ar avalabil
            self.future_values_key_item[cur_key] = {
                "custom_validate_fn": custom_validate_fn,
                "custom_error_fn": custom_error_fn,
                "validator_class": validator_class,
                "validator_config": validator_init_dict,
                "value": raw_value,
                "dependencies": gen_depend_dict,
            }
            # set the data structur for easy accesing dependencies
            for dep in self.future_values_key_item[cur_key]["dependencies"].values():
                if dep not in self.future_values_key_dep:
                    self.future_values_key_dep[dep] = []
                # check for circle ref
                if cur_key in self._get_all_refs(dep):
                    self.add_error("error validating [{section}]{option}: circle reference with [{section_dep}]{option_dep}".format(section=cur_key.section, option=cur_key.option, section_dep=dep.section, option_dep=dep.option))
                    return
                self.future_values_key_dep[dep].append(cur_key)

    def _resolve_dep(self, key):
        """
        this method resolves dependencies for the given key.
        call the method afther the item "key" was added to the list of avalable items
        """
        if key in self.future_values_key_dep:
            # there are some dependencies that can be resoled
            dep_list = self.future_values_key_dep[key]
            del self.future_values_key_dep[key]  # remove dependencies
            also_finish = []
            # iterate over the dependencies that can now be resoled
            for dep in dep_list:
                if self.__resolve_dep_helper(dep, key) is True:
                    also_finish.append(dep)
            # maybe the resolving process leed to new deps that can be resolved
            for dep in also_finish:
                self._resolve_dep(dep)

    def __resolve_dep_helper(self, dep, key):
        # in the item "dep" the dependencie "key" can be resolved
        data = self.future_values_key_item[dep]["dependencies"]
        args = {}
        new_data = {}
        for arg_name, dependent_from in data.items():
            if key == dependent_from:
                args[arg_name] = self.get(dependent_from.section, dependent_from.option)
            else:
                new_data[arg_name] = dependent_from
        self.future_values_key_item[dep]["dependencies"] = new_data
        new_config = self.future_values_key_item[dep]["validator_config"]
        for k, v in args.items():
            new_config[k] = v
        self.future_values_key_item[dep]["validator_config"] = new_config
        if not new_data:
            # resolve this item
            custom_validate_fn = self.future_values_key_item[dep]["custom_validate_fn"]
            custom_error_fn = self.future_values_key_item[dep]["custom_error_fn"]
            try:
                validator = self._get_validator(self.future_values_key_item[dep]["validator_class"], self.future_values_key_item[dep]["validator_config"])
                custom_validate_fn(dep.section, dep.option, validator, self.future_values_key_item[dep]["value"])
                del self.future_values_key_item[dep]
                return True
            except Exception as e:
                custom_error_fn(section=dep.section, option=dep.option, error=e)
        return False

    def _handle_error(self, section, option, error):
        self.add_error("error validating [{section}]{option}: {msg}".format(section=section,
                                                                            option=option,
                                                                            msg=error))

    def add_error(self, error_msg, exception=None):
        logger.debug(error_msg)
        if exception is not None:
            logger.debug(exception)
        self.errors.append(error_msg)

    def _get_all_refs(self, dep, handled_refs=None):
        """
        get al list of all dependencies for the given item "dep"
        """
        if handled_refs is None:
            handled_refs = [dep]
        else:
            if dep in handled_refs:
                return []
        res = []
        if dep in self.future_values_key_item:
            res.extend(
                self.future_values_key_item[dep]["dependencies"].values())
            add = []
            for h_d in res:
                add.extend(self._get_all_refs(h_d, handled_refs))
            res.extend(add)
        return list(set(res))

    def get(self, section, option):
        return self.parsed_values[section][option]

    def has_option(self, section, option):
        if section in self.parsed_values:
            return option in self.parsed_values[section]
        return False

    def add(self, section, option, value):
        if section not in self.parsed_values:
            self.parsed_values[section] = {}
        if option in self.parsed_values[section]:
            logger.warning(
                "override Section:{section} / Option: {option}".format(
                    section=section,
                    option=option))
        self.parsed_values[section][option] = value

    def _get_validator(self, validator_class, validator_init_dict):
        try:
            return validator_class(self, **validator_init_dict)
        except Exception as e:
            raise ParserException(
                "error init validator '{name}'".format(
                    name=validator_class.name),
                e)

    def validate(self, section, option, validator, raw_value):
        self.add(section, option, validator.validate(raw_value))
