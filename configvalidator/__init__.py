# -*- coding: utf-8 -*-

"""
ConfigValidator
~~~~~~~~~~~~~~~~~~~~~
ConfigValidator is an python module to Validate ini File user input.
After validation you will get are well-defined python dict with the corresponding validate user inputs.

To achieve this, you will need an config dict, which is part of your source code.
Furthermore you need an ini file, which is given to the program at runtime.
Both inputs to ConfigValidator will lead in an well-defined python dict,
which can then be used in your program.

usage:
   >> from configvalidator import ConfigValidator
   >> config_dict = {}

   >> cp = ConfigParser()
   >> cp.read("user_input.ini")

   >> cv = ConfigValidator(cp=cp)
   >> data = cv.parse(config_dict=config_dict)


:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

__title__ = 'configvalidator'
__version__ = '0.2.0'
__author__ = 'Jan-Hendrik Dolling'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2015 Jan-Hendrik Dolling'


from configvalidator.tools.basics import remove_data, add_data, load_validator
from configvalidator.tools.exceptions import ConfigValidatorException, ParserException, ValidatorException, InitException, LoadException, ConfigParserException
from configvalidator.tools.configValidator import ConfigValidator
from configvalidator.tools.result import AttributeDict

from configvalidator.validators import load as _load_validators
from configvalidator.features.sections import load as _load_feature_sections
from configvalidator.features.options import load as _load_feature_options

#from configvalidator.tools.configParser import ConfigParser

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):

        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

# load features and validators
_load_validators()
_load_feature_sections()
_load_feature_options()
