from configvalidator import Validator

class Demo(Validator):
    name = "EV2"

    def validate(self, value):
        return True

    def transform(self, value):
        return value
