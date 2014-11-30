# configvalidator

python module to Validate ini File user input


## Get Started

    $ pip install configvalidator

``` python
from configvalidator import ConfigValidator
```

## Example

imagine the following ini file

``` text
[Section A]
option1 = Hello Welt
option2 = 50

```
and the following validator dict

``` python
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
}
```

after parsing the values. The result looks as following:

``` python
values = ConfigValidator(ini_file, ini_validator).parse()

assert values["SectionA"]["option1"] == "Hello Welt"
assert values["SectionA"]["option2"] == 50
assert values["SectionB"]["option1"] == 100
```
