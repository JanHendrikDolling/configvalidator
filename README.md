# configvalidator

python module to Validate ini File user input


## Get Started

    $ pip install configvalidator
    $ from configvalidator import ConfigValidator

## Example


``` python
ini_validator = {
    "Section A": {
        "option 1": {
            "default": "127.0.0.1",
            "validator": "TRUE",
        },
        "option 2": {
            "validator": "INT",
        },
    },
    "Section B": {
        "option 1":{
            "return": lambda x: int(x),
            "default": 100,        
    },  
}

values = ConfigValidator(ini_file, ini_validator)
```


