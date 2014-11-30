ini_validator = {
    "SectionA": {
        "option1": {
            "default": "127.0.0.1",
            "validator": "TRUE",
        },
        "option2": {
            "validator": "INT",
        },
    },
    "SectionB": {
        "option1":{
            "return": lambda x: int(x),
            "default": 100,
        },      
    },  
}

from configvalidator import ConfigValidator
values = ConfigValidator("file.ini", ini_validator).parse()

assert values["SectionA"]["option1"] == "Hello Welt"
assert values["SectionA"]["option2"] == 50
assert values["SectionB"]["option1"] == 100

