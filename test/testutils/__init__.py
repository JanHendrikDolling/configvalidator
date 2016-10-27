# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

try:
    from ordereddict import OrderedDict
except ImportError:
    from collections import OrderedDict
from configvalidator import ConfigValidator
from six.moves import configparser
import os


class CPStub(object):
    def __init__(self, data_dict=None):
        if data_dict is None:
            data_dict = get_dict()
        self._data = data_dict

    def has_option(self, section, option):
        return section in self._data and option in self._data[section]

    def get(self, section, option):
        return self._data[section][option]

    def options(self, section):
        return self._data[section].keys()

    def add(self, section, option, value):
        if section not in self._data:
            self._data[section] = get_dict()
        self._data[section][option] = value

class CPStub2(CPStub):

    def __init__(self, data_dict=None):
        super(CPStub2, self).__init__(data_dict)

    def read(self, ini_path):
        config = configparser.RawConfigParser()
        config.read(ini_path)
        self._data = get_dict()
        for section in config.sections():
            if section not in self._data:
                self._data[section] = get_dict()
            for option in config.options(section):
                self._data[section][option] = config.get(section, option)

class CPStub3(CPStub):

    def __init__(self, data_dict=None):
        super(CPStub3, self).__init__(data_dict)

    def read(self, ini_path):
        pass


class CPStub4(CPStub3):
    pass

def get_valid_stub(data=None):
    sp = CPStub(data)
    sp.read = lambda x: x
    return sp

def get_cp(data=None):
    stub = get_valid_stub(data)
    return ConfigValidator(stub)

def get_dict():
    return OrderedDict()

def get_test_utils_base():
    cwd = os.getcwd()
    file = os.path.dirname(__file__)
    if file.startswith(cwd):
        if os.path.exists(os.path.join(cwd, "testutils")):
            return "testutils"
        elif os.path.exists(os.path.join(cwd, "test", "testutils")):
            return os.path.join("test", "testutils")
        else:
            raise Exception("do not find testdata")
    else:
        raise Exception("cwd should be / or /test")