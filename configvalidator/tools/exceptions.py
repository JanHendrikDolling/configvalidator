# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""
from six import string_types


class ConfigValidatorException(Exception):

    """
    base class for all ConfigValidator Exceptions
    """
    def __init__(self, error_msg, exception=None):
        assert isinstance(error_msg, string_types)
        assert isinstance(exception, Exception) or exception is None
        self._errors = [(error_msg, exception)]

    @property
    def info(self):
        return [x for x, _ in self._errors]

    @property
    def errors(self):
        return self._errors

    def add(self, validator_exception):
        assert isinstance(validator_exception, ValidatorException)
        self._errors.extend(validator_exception.errors)

    @classmethod
    def from_list(cls, l):
        assert isinstance(l, list)
        assert len(l) > 0
        exc_l = []
        for item in l:
            if isinstance(item, string_types):
                exc_l.append(ValidatorException(item))
            elif isinstance(item, ValidatorException):
                exc_l.append(item)
            else:
                assert len(item) == 2
                assert isinstance(item[1], Exception)
                exc_l.append(ValidatorException(item[0], item[1]))
        v = exc_l[0]
        for x in exc_l[1:]:
            v.add(x)
        return v

    def __str__(self):
        return "\n".join(self.info)
    
    @property
    def message(self):
        return self.__str__()


class InitException(ConfigValidatorException):

    """
    TODO
    """
    pass


class LoadException(ConfigValidatorException):

    """
    TODO
    """
    pass


class ParserException(ConfigValidatorException):

    """
    TODO
    """
    def __init__(self, error_msg, exception=None):
        assert isinstance(error_msg, string_types)
        assert isinstance(exception, Exception) or exception is None
        self.error_msg = error_msg
        self.exception = exception

    def __str__(self):
        if self.exception is None:
            return self.error_msg
        else:
            return "{msg} | {error}".format(msg=self.error_msg, error=self.exception)


class ValidatorException(ConfigValidatorException):

    """
    TODO
    """
    pass

class ConfigParserException(ConfigValidatorException):
    pass

