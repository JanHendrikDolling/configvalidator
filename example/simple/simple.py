# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

config_dict = {
    "SectionA": {
        "option1": {
            "default": "This is the default value",
        },
        "option2": {
            "validator": "int",
        },
    },
    "SectionB": {
        "option1":{
            "validator": {
                "type": "int",
                "max": 100,
            },
            "default": 100,
        },      
    },  
}

from six.moves import configparser
from configvalidator import ConfigValidator

# ini config parser
cp1 = configparser.RawConfigParser()
cp1.read("file1.ini")

# init config validator
cv1 = ConfigValidator(cp=cp1)
values1 = cv1.parse(config_dict=config_dict)

assert values1["SectionA"]["option1"] == "Hello Welt"
assert values1["SectionA"]["option2"] == 50
assert values1["SectionB"]["option1"] == 100

# ini config parser
cp2 = configparser.RawConfigParser()
cp2.read("file2.ini")

# init config validator
cv2 = ConfigValidator(cp=cp2)
values2 = cv2.parse(config_dict=config_dict)

assert values2["SectionA"]["option1"] == "This is the default value"
assert values2["SectionA"]["option2"] == 55
assert values2["SectionB"]["option1"] == 100



