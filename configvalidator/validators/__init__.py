# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

import os
import json
import itertools
import datetime
import re
import random
import string
import logging
from configvalidator.tools.exceptions import ParserException, ValidatorException, ConfigValidatorException, InitException
from configvalidator.tools.basics import Validator, load_validator_form_dict
from configvalidator.tools.timezone import TZ
from six import string_types
from six.moves.urllib.parse import urlparse
import socket


logger = logging.getLogger(__name__)


def load():
    pass


class DefaultValidator(Validator):

    """Validator there all import are permitted

This validator represents the identity. The validation result is always true.

 * This validator has no required parameter.
 * This validator has no optional parameter.

    """
    name = "default"

    def validate(self, value):
        """determine if one input satisfies this validator.

        call the transform method and return True if no Exception occure.

        Args:
            value (String): the value to check if it suffused this Validator

        Returns:
            The value
        """
        return value


class ErrorValidator(Validator):

    """
    this validator is used, it something went wrong during another validator initialization.
    this validator always fails
    """
    name = "error"

    def __init__(self, error_msg):
        self.error_msg = error_msg

    def validate(self, value):
        raise ValidatorException(self.error_msg)


class StringValidator(Validator):
    """
This validator checks, if the input is an string. 

 * This validator has no required parameter.
 * This validator has the following optional parameter.
    * min_length: the minimum string length (int)
    * max_length: the maximum string length (int)
    """
    name = "str"

    def __init__(self, min_length=None, max_length=None, characters=None, first=None):
        self.min = min_length
        self.max = max_length
        i = IntValidator()
        try:
            if min_length is not None:
                i.validate(str(min_length))
        except:
            raise InitException("min_length must be a number")
        try:
            if max_length is not None:
                i.validate(str(max_length))
        except:
            raise InitException("max_length must be a number")
        self.allowed_characters = characters
        self.first_characters = first
        assert isinstance(self.allowed_characters, list) or self.allowed_characters is None
        assert isinstance(self.first_characters, list) or self.first_characters is None

    def validate(self, value):
        errors = []
        try:
            self._validate_length(len(value))
        except ValidatorException as e:
            errors.extend(e.info)
        if self.first_characters is not None and len(value) > 0:
            if value[0] not in self.first_characters:
                errors.append("the fisrt character must be one of: {items}".format(items=self.first_characters))
        if self.allowed_characters is not None:
            for c in value:
                if c not in self.allowed_characters:
                    errors.append("allowed characters: {items}".format(items=self.allowed_characters))
                    break
        if len(errors) > 0:
            raise ValidatorException.from_list(errors)
        return value

    def _validate_length(self, value, error_msg=" string length"):
        errors = []
        if self.min is not None:
            if value < self.min:
                errors.append(
                    "minimum{error_msg}: {min}".format(
                        error_msg=error_msg,
                        min=self.min))
        if self.max is not None:
            if value > self.max:
                errors.append(
                    "maximum{error_msg}: {max}".format(
                        error_msg=error_msg,
                        max=self.max))
        if len(errors) > 0:
            raise ValidatorException.from_list(errors)
        return value


class EmptyValidator(Validator):
    name = "empty"

    def validate(self, value):
        if value != "":
            raise ValidatorException("The input is not Empty.")
        return ""


class NotEmptyValidator(StringValidator):
    name = "not-empty"

    def __init__(self):
        super(NotEmptyValidator, self).__init__(min_length=1)

    def _validate_length(self, value):
        if value == 0:
            raise ValidatorException("The input is Empty.")

class IntValidator(StringValidator):
    """
This validator checks, if the input is an int. 

 * This validator has no required parameter.
 * This validator has the following optional parameter.
    * min: the minimum input int (int)
    * max: the maximum input int (int)
    """
    name = "int"

    def __init__(self, min=None, max=None):
        self.min = None
        self.max = None
        if min is not None:
            try:
                self.min = self.transform(str(min))
            except Exception:
                raise InitException("min must be a number")
        if max is not None:
            try:
                self.max = self.transform(str(max))
            except Exception:
                raise InitException("max must be a number")

    def validate(self, value):
        try:
            return self._validate_length(self.transform(value), error_msg="")
        except ConfigValidatorException:
            raise
        except Exception as e:
            raise ValidatorException(
                "Input is no {name}".format(name=self.name),
                e)

    def transform(self, value):
        return int(value)


class FloatValidator(IntValidator):
    """
This validator checks, if the input is an float.

 * This validator has no required parameter.
 * This validator has the following optional parameter.
    * min: the minimum input int (float)
    * max: the maximum input int (float)


    """
    name = "float"

    def transform(self, value):
        return float(value)


class BoolValidator(DefaultValidator):
    """
This validator checks, if the input is an boolean. 

 * This validator has no required parameter.
 * This validator has no optional parameter.

The following values are  (not case insensitive)
true  | false
------------- | -------------
yes  | no
y    | n
true | false
t    | f
1    | 0
    """
    name = "bool"
    values_true = ["yes", "y", "true", "t", "1"]
    values_false = ["no", "n", "false", "f", "0"]

    def validate(self, value):
        allowed_values = list(
            itertools.chain(*zip(self.values_true, self.values_false)))
        if value.lower() not in allowed_values:
            raise ValidatorException(
                "allowed values: {allowed_values}".format(allowed_values=", ".join(allowed_values)))
        return value.lower() in self.values_true


class JsonValidator(DefaultValidator):
    """
This validator checks, if the input is an json Serialized string. 

 * This validator has no required parameter.
 * This validator has no optional parameter.
    """
    name = "json"

    def validate(self, value):
        try:
            return json.loads(value)
        except Exception as e:
            raise ValidatorException("Invalid json input", e)


class PathValidator(DefaultValidator):
    """
This validator checks, if the input is an existing path (file or directory). 

 * This validator has no required parameter.
 * This validator has the following optional parameter.
    * absolute: required an absolute path. The default ist False.  (boolean)
    * allowed_prefix: a list of allowed prefixes for this path. (list of paths)
    * disallowed_prefix: a list of disallowed prefixes for this path. (list of paths)

    """
    name = "path"

    def __init__(
            self,
            absolute=None,
            allowed_prefix=None,
            disallowed_prefix=None):
        super(PathValidator, self).__init__()
        self._absolute = None if absolute is None else absolute is True
        self._allowed_prefix = allowed_prefix
        self._disallowed_prefix = [] if disallowed_prefix is None else disallowed_prefix
        if isinstance(self._allowed_prefix, string_types):
            self._allowed_prefix = [self._allowed_prefix]
        if isinstance(self._disallowed_prefix, string_types):
            self._disallowed_prefix = [self._disallowed_prefix]
        try:
            assert isinstance(self._allowed_prefix, list) or self._allowed_prefix is None
        except AssertionError:
            raise InitException("invalid allowed_prefix input")
        try:
            assert isinstance(self._disallowed_prefix, list)
        except AssertionError:
            raise InitException("invalid disallowed_prefix input")

    def validate(self, value):
        errors = []
        try:
            if os.path.exists(value):
                if self._absolute is not None:
                    if os.path.isabs(value) != self._absolute:
                        if os.path.isabs(value) is True:
                            errors.append("path \"{path}\" is absolute but must be relative".format(path=value))
                        else:
                            errors.append("path \"{path}\" is relative but must be absolute".format(path=value))
                if self._allowed_prefix is not None:
                    status = False
                    for prefix in self._allowed_prefix:
                        status = status or value.startswith(prefix)
                    if status is False:
                        errors.append("path \"{path}\" is not in allowed prefixes".format(path=value))
                for prefix in self._disallowed_prefix:
                    if value.startswith(prefix):
                        errors.append(
                            "prefix: ({prefix}) not allowed".format(prefix=prefix))
            else:
                errors.append("path \"{path}\" doesn't exist".format(path=value))
        except Exception as e:
            errors.append("Error: {msg}".format(msg=str(e)))
        if len(errors) > 0:
            raise ValidatorException.from_list(errors)
        return value


class FileValidator(PathValidator):
    """
This validator checks, if the input is an existing File. 
Extending the *path* validator.

 * No additional required or optional parameters.


    """
    name = "file"

    def __init__(
            self,
            absolute=None,
            allowed_prefix=None,
            disallowed_prefix=None):
        super(
            FileValidator,
            self).__init__(
            absolute,
            allowed_prefix,
            disallowed_prefix)

    def validate(self, value):
        super(FileValidator, self).validate(value)
        if not os.path.isfile(value):
            raise ValidatorException("path \"{path}\" is not an file".format(path=value))
        return value


class DirValidator(PathValidator):
    """
This validator checks, if the input is an existing directory. 
Extending the *path* validator.

 * This validator has additional required parameter.
 * This validator has the following additional optional parameter.
    * include_dirs: a list of dirs that must exist. (list of relativ paths)
    * include_files: a list of files that must exist. (list of relativ paths)
    * exclude_dirs: a list of dirs that are excluded. (list of relativ paths)
    * exclude_files: a list of files that are excluded. (list of relativ paths)

    """
    name = "dir"

    def __init__(
        self,
        include_dirs=None,
        include_files=None,
        exclude_dirs=None,
        exclude_files=None,
            **kwargs):
        super(DirValidator, self).__init__(**kwargs)
        self._include_dirs = include_dirs if include_dirs is not None else []
        assert isinstance(self._include_dirs, list)
        self._include_files = include_files if include_files is not None else [
        ]
        assert isinstance(self._include_files, list)
        self._exclude_dirs = exclude_dirs if exclude_dirs is not None else []
        assert isinstance(self._exclude_dirs, list)
        self._exclude_files = exclude_files if exclude_files is not None else [
        ]
        assert isinstance(self._exclude_files, list)

    def validate(self, value):
        errors = []
        super(DirValidator, self).validate(value)
        if not os.path.isdir(value):
            raise ValidatorException("path \"{path}\" is not an directory.".format(path=value))
        for item in itertools.chain(self._include_dirs, self._include_files):
            if not os.path.isabs(item):
                item = os.path.join(value, item)
            if not os.path.exists(item):
                errors.append("path dosen't \"{path}\" exist".format(path=item))
        for item in itertools.chain(self._exclude_dirs, self._exclude_files):
            if not os.path.isabs(item):
                item = os.path.join(value, item)
            if os.path.exists(item):
                errors.append("path \"{path}\" exist".format(path=item))
        if len(errors) > 0:
            raise ValidatorException.from_list(errors)
        return value


class PortValidator(IntValidator):
    """
This validator checks, if the input is a vailed port. 

 * This validator has no required parameter.
 * This validator has no optional parameter.

    """
    name = "port"

    def __init__(self, allow_null=True):
        self.allow_null = allow_null
        if allow_null is True:
            min = 0
        else:
            min = 1
        max = 65535
        super(PortValidator, self).__init__(min=min, max=max)

    def validate(self, value):
        try:
            return super(PortValidator, self).validate(value)
        except:
            if self.allow_null is True:
                raise ValidatorException("port range [0-65535]")
            else:
                raise ValidatorException("port range [1-65535]")


class RegexValidator(Validator):
    """
This validator checks, if the input matches a given regular expression. 

 * This validator has following required parameter.
    * pattern: the regular expression. (string)
 * This validator has the following optional parameter.
    * flags: modify the expression’s behaviour (int) 

    """
    name = "regex"

    def __init__(self, pattern, flags=0):
        super(RegexValidator, self).__init__()
        try:
            self._pattern = re.compile(pattern, flags)
        except Exception as e:
            raise InitException("error init regex: {msg}".format(msg=e))

    def validate(self, value):
        try:
            if self._pattern.match(value) is None:
                raise ValidatorException("No Matching")
        except ConfigValidatorException:
            raise
        except Exception as e:
            raise ValidatorException("Unknown Error", e)
        return value


class EmailValidator(RegexValidator):
    """
This validator checks, if the input is a vailed Email. 

 * This validator has no required parameter.
 * This validator has the following optional parameter.
    * hostname: a list of allowed host names (list)

    """
    name = "email"

    def __init__(self, hostname=None):
        self._hostname = hostname
        assert isinstance(self._hostname, list) or self._hostname is None
        if self._hostname is not None:
            self._hostname = [x.lower() for x in self._hostname]
        super(EmailValidator, self).__init__(pattern=r"[^@]+@[^@]+\.[^@]+",
                                             flags=re.IGNORECASE)

    def validate(self, value):
        try:
            super(EmailValidator, self).validate(value)
        except ValidatorException:
            raise ValidatorException("invalid email format")
        if self._hostname is not None:
            _, host = value.split("@")
            if host.lower() not in self._hostname:
                raise ValidatorException("invalid host")
        return value


class OrValidator(Validator):

    """Validator with are list of Validator's - to bee True
    one of them must be True

This validator checks, multiple validators. This validator is true if one of the validatos is true. 

 * This validator has following required parameter.
    * validators: this is a list of validator configurations. The validator configuration is either a dict or a string. (list)
 * This validator has the following optional parameter.
    * kwargs: this is a dict of global kwargs, that will be passed to all the validators in the *validators* list. (dict)


    Attributes:
        validators (List): List of validators to check
    """
    name = "or"

    def __init__(self, validators, kwargs=None, **dependencies):
        """Inits OrValidator

        evalutest the entry "validator_OR" from the ini_validator dict.
        This entry contains a list with Validator names.
        This validators are loaded.

        Raises:
            ConfigValidatorException: if a Validator from "validator_OR"
                                      can't bee instanced
        """
        super(OrValidator, self).__init__()
        assert isinstance(validators, list)
        if kwargs is None:
            kwargs = {}
        assert isinstance(kwargs, dict)
        # transform validators to dict config
        validators_transformed = []
        for val in validators:
            if isinstance(val, string_types):
                validators_transformed.append({
                    "type": val,
                })
            else:
                assert isinstance(val, dict)
                validators_transformed.append(val)
        # assign dependencies
        for k, v in dependencies.items():
            fond = False
            if "_" in k:
                validator_name, arg_name = k.split("_", 1)
                for validator_config in validators_transformed:
                    if validator_config["type"] == validator_name:
                        validator_config[arg_name] = v
                        fond = True
            if fond is False:
                kwargs[k] = v
        for k, v in kwargs.items():
            new_validators_transformed = []
            for item in validators_transformed:
                item[k] = v
                new_validators_transformed.append(item)
            validators_transformed = new_validators_transformed
        # get validators
        self._validators = []
        self._used_validator = []
        for item in validators_transformed:
            val_class, kwarg_dict = load_validator_form_dict({"validator": item})
            val_inst = val_class(**kwarg_dict)
            # set data for this validator
            val_inst.data = self.data
            self._validators.append(val_inst)

    def validate(self, value):
        """validate function form OrValidator

        Returns:
            True if at least one of the validators
            validate function return True
        """
        errors = []
        self._used_validator = []
        for val in self._validators:
            try:
                val.validate(value)
                self._used_validator.append(val)
            except ValidatorException as e:
                errors.append(e)
            except Exception as e:
                errors.append(ValidatorException("Unknown Error", e))
        if len(self._used_validator) == 0:
            raise ValidatorException.from_list(errors)
        return value


class AndValidator(OrValidator):
    """
This validator checks, multiple validators. This validator is true if all of the validatos are true. 

The parameters are the same as the *or* validator. 

    """
    name = "and"

    def validate(self, value):
        """validate function form OrValidator

        Returns:
            True if at least one of the validators
            validate function return True
        """
        errors = []
        self._used_validator = []
        for val in self._validators:
            try:
                val.validate(value)
                self._used_validator.append(val)
            except ValidatorException as e:
                errors.append(e)
            except Exception as e:
                errors.append(ValidatorException("Unknown Error", e))
        if len(errors) > 0:
            raise ValidatorException.from_list(errors)
        return value


class OneOffValidator(OrValidator):
    """The Validator has the exact same interface as the or Validator
    but it will return the result from the first validator that validates the input.
    """
    name = "one-off"

    def validate(self, value):
        errors = []
        for val in self._validators:
            try:
                return val.validate(value)
            except ValidatorException as e:
                errors.append(e)
            except Exception as e:
                errors.append(ValidatorException("Unknown Error", e))
        raise ValidatorException.from_list(errors)


class UrlValidator(Validator):
    """
This validator checks, if the input matches a URL. 

 * This validator has no required parameter.
 * This validator has the following optional parameter.
    * scheme: a list of vailed url schemes (list)
    * hostname: a list of vailed host names (list)
    * port: a list of vailed ports (list)
    * allow_fragments: see urlparse docs (bool) 

If no parameter is specified any vailed URL will pass.
If scheme is only one item it will be passed to urlparse as scheme argument.


    """
    name = "url"

    SCHEME_PORT_MAPPING = {
        "file": None,
        "ftp": 21,
        "gopher": 70,
        "hdl": None,
        "http": 80,
        "https": 443,
        "imap": 143,
        "mailto": None,
        "mms": 654,
        "news": None,
        "nntp": 119,
        "prospero": None,
        "rsync": 873,
        "rtsp": 554,
        "rtspu": None,
        "sftp": 22,
        "shttp": 80,
        "sip": 5060,
        "sips": 5061,
        "snews": None,
        "svn": 3690,
        "svn+ssh": 22,
        "telnet": 23,
        "wais": None,
    }

    def __init__(self, scheme=None, hostname=None, port=None, add_default_port=False):
        super(UrlValidator, self).__init__()
        if scheme is None:
            self._url_scheme = None
        else:
            assert isinstance(scheme, list)
            self._url_scheme = [x.lower() for x in scheme]
        if hostname is not None:
            assert isinstance(hostname, list)
            self._hostname = [x.lower() for x in hostname]
        else:
            self._hostname = None
        self._port = port
        assert isinstance(port, list) or self._port is None
        self.add_default_port = add_default_port is True

    def validate(self, value):
        errors = []
        try:
            o = urlparse(value)
            if ":" in o.netloc:
                host, port = o.netloc.rsplit(":", 1)
                port = int(port)
            else:
                host = o.netloc
                port = None
            if o.scheme in UrlValidator.SCHEME_PORT_MAPPING:
                default_port = UrlValidator.SCHEME_PORT_MAPPING[o.scheme]
            else:
                default_port = None
            # copy _port list because there are will be maybe some ports added
            if self._port is not None:
                check_ports = list(self._port)
            else:
                check_ports = None
            if default_port is not None:
                if self.add_default_port is True:
                    if check_ports is None:
                        check_ports = []
                    check_ports.append(default_port)
            if self._hostname is not None:
                if host not in self._hostname:
                    errors.append("host nor allowed")
            if self._url_scheme is not None:
                if o.scheme.lower() not in self._url_scheme:
                    errors.append("scheme not allowed")
            if check_ports is not None:
                # check if port is allowed
                check_port = port if port is not None else default_port
                if check_port not in check_ports:
                    errors.append("port not allowed")
        except Exception as e:
            errors.append(ValidatorException("Unknown Error", e))
        if len(errors) > 0:
            raise ValidatorException.from_list(errors)
        return value


class IPv4Validator(Validator):
    """
This validator checks, if the input is a vailed IPv4 adress. 

 * This validator has no required parameter.
 * This validator has the following optional parameter.
    * private: only private network ip addresses are valid inputs. Default ist False. (bool)
    * cidr: checks if the ip belongs to this network. Default is "0.0.0.0/0"


    """
    name = "ipv4"

    def __init__(self, private=False, cidr="0.0.0.0/0"):
        try:
            self._private = private is True
            try:
                ip, subnet_mask = cidr.split("/")
                if ip == "":
                    ip = "0.0.0.0"
            except:
                raise InitException("cidr format error | IP/CIDR or /CIDR")
            self._network = IPv4Validator.ip_to_bit_str(ip)
            self._subnet_mask = IPv4Validator.subnet_mask_int_to_bit(
                int(subnet_mask))
            self._private_network_list = []
            self._private_network_list.append((
                IPv4Validator.ip_to_bit_str("10.0.0.0"),
                IPv4Validator.subnet_mask_int_to_bit(8)
            ))
            self._private_network_list.append((
                IPv4Validator.ip_to_bit_str("172.16.0.0"),
                IPv4Validator.subnet_mask_int_to_bit(12)
            ))
            self._private_network_list.append((
                IPv4Validator.ip_to_bit_str("192.168.0.0"),
                IPv4Validator.subnet_mask_int_to_bit(16)
            ))
        except InitException:
            raise
        except Exception as e:
            raise InitException(str(e))

    @staticmethod
    def _split_ip_adress(ipv4_str):
        res = ipv4_str.split(".")
        if len(res) == 4:
            for item in res:
                status = True
                try:
                    status = not 0 <= int(item) < 256 or str(int(item)) != item
                finally:
                    if status is True:
                        raise ValidatorException("invalid ipv4 format: [0-255] | no leading zeros")
        else:
            raise ValidatorException(
                "IP format: [0-255].[0-255].[0-255].[0-255]")
        return int(res[0]), int(res[1]), int(res[2]), int(res[3])

    @staticmethod
    def ip_to_bit_str(ipv4_str):
        def _gen_prefix(v):
            return "".join(["0" for _ in range(8 - len("{b:b}".format(b=v)))])

        b1, b2, b3, b4 = IPv4Validator._split_ip_adress(ipv4_str)
        return "{p_b1}{b1}.{p_b2}{b2}.{p_b3}{b3}.{p_b4}{b4}".format(
            p_b1=_gen_prefix(b1), b1="{b:b}".format(b=b1),
            p_b2=_gen_prefix(b2), b2="{b:b}".format(b=b2),
            p_b3=_gen_prefix(b3), b3="{b:b}".format(b=b3),
            p_b4=_gen_prefix(b4), b4="{b:b}".format(b=b4),
        )

    @staticmethod
    def subnet_mask_int_to_bit(subnet_mask):
        assert 0 <= subnet_mask <= 32
        res = ""
        for r in range(subnet_mask):
            res += "1"
            if r % 8 == 7 and r != 31:
                res += "."
        return res

    def validate(self, value):
        try:
            value_bit_str = IPv4Validator.ip_to_bit_str(value)
            IpValidator.validate_bits(ip_bit_str=value_bit_str,
                                      network=self._network,
                                      subnet_mask_bit_str=self._subnet_mask,
                                      private_network_list=None if self._private is False else self._private_network_list)
        except ValidatorException:
            raise
        except Exception as e:
            raise ValidatorException("Unknown Error", e)
        return value


class Ipv6Validator(Validator):
    """
This validator checks, if the input is a vailed IPv6 adress. 

 * This validator has no required parameter.
 * This validator has the following optional parameter.
    * private: only private network ip addresses are valid inputs. Default ist False. (bool)
    * cidr: checks if the ip belongs to this network. Default is "::/0"
    * host_subnet_mask: allowed /128 at the end of an valid ipv6 address. Default False (bool)

    """
    name = "ipv6"

    def __init__(self, private=False, cidr="::/0", host_subnet_mask=False):
        try:
            self._private = private is True
            self._host_subnet_mask = host_subnet_mask is True
            try:
                ip, subnet_mask = cidr.split("/")
                if ip == "":
                    ip = "::"
            except:
                raise InitException("cidr format error | IP/CIDR or /CIDR")
            self._network = Ipv6Validator.ip_to_bit_str(ip)
            self._subnet_mask = Ipv6Validator.subnet_mask_int_to_bit(
                int(subnet_mask))
            self._private_network_list = []
            self._private_network_list.append((
                Ipv6Validator.ip_to_bit_str("fc00::"),
                Ipv6Validator.subnet_mask_int_to_bit(7)
            ))
            self._private_network_list.append((
                Ipv6Validator.ip_to_bit_str("::1"),
                Ipv6Validator.subnet_mask_int_to_bit(128)
            ))
            self._private_network_list.append((
                Ipv6Validator.ip_to_bit_str("fe80::"),
                Ipv6Validator.subnet_mask_int_to_bit(10)
            ))
        except InitException:
            raise
        except Exception as e:
            raise InitException(str(e))

    @staticmethod
    def _split_ip_adress(ipv6_str, host_subnet_mask=False):
        assert isinstance(ipv6_str, string_types)
        if host_subnet_mask is True:
            if "/" in ipv6_str:
                ipv6_str, subnet_mask = ipv6_str.split("/")
                if subnet_mask != "128":
                    raise ValidatorException("if subnet mask is given it must be 128!")
        elif "/" in ipv6_str:
            raise ValidatorException("error: host subnet mask not allowed")
        if "#" in ipv6_str or ":" not in ipv6_str:
            raise ValidatorException("invalid ipv6 format")
        if "::" in ipv6_str:
            ipv6_str = ipv6_str.replace("::", "#")
            reduction = True
        else:
            reduction = False
        data = [x for x in ipv6_str.split(":")]
        if "." in data[-1]:
            # handle input -> ::x.x.x.x
            if data[-1].startswith("#"):
                ipv4 = data[-1][1:]
                start_with = "#"
            else:
                ipv4 = data[-1]
                start_with = ""
            IPv4Validator().validate(ipv4)
            # transform ipv4 suffix to hex format
            ipv4_bit_string_suffix = IPv4Validator.ip_to_bit_str(ipv4)
            b1, b2, b3, b4 = ipv4_bit_string_suffix.split(".")
            data[-1] = "{start_with}{ip_item:x}".format(start_with=start_with, ip_item=int("{b1}{b2}".format(b1=b1, b2=b2), 2))
            data.append("{0:x}".format(int("{b3}{b4}".format(b3=b3, b4=b4), 2)))
        if reduction is True:
            new = []
            resolved = False
            for item in data:
                if "#" in item:
                    if resolved is True or item.count("#") > 1:
                        raise ValidatorException("invalid ipv6 syntax: only one reduction via ::")
                    resolved = True
                    count = len(data)
                    prefix, suffix = item.split("#")
                    if prefix != "":
                        new.append(prefix)
                        count += 1
                    if suffix != "":
                        count += 1
                    for _ in range(9 - count):
                        new.append("0")
                    if suffix != "":
                        new.append(suffix)
                else:
                    new.append(item)
            data = new
        assert "#" not in "".join(data)
        if len(data) != 8:
            raise ValidatorException("invalid IPv6 address - just 8 blocks")
        res = []
        for item in data:
            try:
                bit_str = bin(int(item, 16))[2:]
                if len(bit_str) > 16:
                    raise ValidatorException("each ipv6 block has maximum 16 bits")
                bit_str = bit_str.zfill(16)
                res.append(bit_str)
            except Exception as e:
                raise ValidatorException("invalid ipv6 syntax: {msg}".format(msg=e))
        return tuple(res)

    @staticmethod
    def ip_to_bit_str(ipv6_str, host_subnet_mask=False):
        res = ""
        for item in Ipv6Validator._split_ip_adress(ipv6_str, host_subnet_mask):
            b = "{0:b}".format(int("{b}".format(b=item), 2))
            res += "{p_b}{b}.".format(
                p_b="".join(["0" for _ in range(16 - len("{b}".format(b=b)))]),
                b=b,
            )
        return res[:-1]

    @staticmethod
    def subnet_mask_int_to_bit(subnet_mask):
        assert 0 <= subnet_mask <= 128
        res = ""
        for r in range(subnet_mask):
            res += "1"
            if r % 16 == 15 and r != 127:
                res += "."
        return res

    def validate(self, value):
        try:
            value_bit_str = Ipv6Validator.ip_to_bit_str(value, self._host_subnet_mask)
            IpValidator.validate_bits(ip_bit_str=value_bit_str,
                                      network=self._network,
                                      subnet_mask_bit_str=self._subnet_mask,
                                      private_network_list=None if self._private is False else self._private_network_list)
        except ValidatorException:
            raise
        except Exception as e:
            raise ValidatorException("Unknown Error", e)
        return value


class IpValidator(OrValidator):
    """
This validator checks, if the input is a vailed IP adress. 
Checks if the input is either *ipv4* or *ipv6*.

 * This validator has no required parameter.
 * This validator has the following optional parameter.
    * private: only private network ip addresses are valid inputs. Default ist False. (bool)
    * ipv4_cidr: checks if the ip (if ipv4) belongs to this network. Default is "0.0.0.0/0"
    * ipv6_cidr: checks if the ip (if ipv6) belongs to this network. Default is "::/0"
    * host_subnet_mask: allowed /128 at the end of an valid ipv6 address. Default False (bool)


    """
    name = "ip"

    def __init__(
        self,
        private=False,
        ipv4_cidr="0.0.0.0/0",
        ipv6_cidr="::/0",
            host_subnet_mask=False):
        super(IpValidator, self).__init__(validators=[
            {
                "type": "ipv4",
                "private": private,
                "cidr": ipv4_cidr,
            },
            {
                "type": "ipv6",
                "private": private,
                "cidr": ipv6_cidr,
                "host_subnet_mask": host_subnet_mask,
            }])

    @staticmethod
    def check_ip_in_network(network, subnet_mask, ip):
        return network[0:len(subnet_mask)] == ip[0:len(subnet_mask)]

    @staticmethod
    def validate_bits(
        ip_bit_str,
        network,
        subnet_mask_bit_str,
            private_network_list=None):
        # check if network mask match
        if not IpValidator.check_ip_in_network(network, subnet_mask_bit_str, ip_bit_str):
            raise ValidatorException("IP outsite of subnet mask")
        if private_network_list is not None:
            # check private network
            for _network, _subnet_mask in private_network_list:
                if IpValidator.check_ip_in_network(_network, _subnet_mask, ip_bit_str):
                    return
            raise ValidatorException("IP is not en private Network")


class GeneralizedTimeValidator(Validator):
    """
    """
    name = "generalizedTime"

    def validate(self, value):
        format_str = "input: YYYYMMDDHH[MM[SS[.fff]]] | YYYYMMDDHH[MM[SS[.fff]]]Z | YYYYMMDDHH[MM[SS[.fff]]]+-HHMM"
        try:
            year = int(value[0:4])
            month = int(value[4:6])
            day = int(value[6:8])
            hour = int(value[8:10])
            minute = 0
            second = 0
            microsecond = 0
            tzinfo = None
            start = 10
            try:
                if len(value) > start + 1 and value[start] not in ["-", "+"]:
                    minute = int(value[10:12])
                    start = 12
                    if len(value) > start + 1:
                        second = int(value[start:14])
                        start = 14
                        if len(value) > start + 1:
                            assert value[start] == "."
                            microsecond = int(value[start + 1:18])
                            start = 18
            except:
                pass
            if len(value) > start:
                if value[start] == "Z":
                    tzinfo = TZ()
                else:
                    if value[start] == "+":
                        diff = 1
                    elif value[start] == "-":
                        diff = -1
                    else:
                        raise ValidatorException(format_str)
                    diff_hour = int(value[start + 1:start + 3])
                    diff_minute = int(value[start + 3:start + 5])
                    tzinfo = TZ(
                        hours=diff *
                        diff_hour,
                        minutes=diff *
                        diff_minute)
            try:
                return datetime.datetime(year=year,
                                         month=month,
                                         day=day,
                                         hour=hour,
                                         minute=minute,
                                         second=second,
                                         microsecond=microsecond,
                                         tzinfo=tzinfo)
            except ValueError as e:
                raise ValidatorException(e.args[0], e)
        except ValidatorException:
            raise
        except Exception as e:
            raise ValidatorException(format_str, exception=e)

class Base64Validator(DefaultValidator):
    """
    """
    name = "base64"

    def __init__(self, encoding="utf-8"):
        self.encoding = encoding
    
    def validate(self, value):
        import base64
        try:
            res = base64.b64decode(value)
        except Exception as e:
            raise ValidatorException(error_msg="invalid base64 string", exception=e)
        try:
            if isinstance(res, bytes) and self.encoding is not None:
                return res.decode(self.encoding)
            else:
                return res
        except Exception as e:
            raise ValidatorException(error_msg="Encoding error", exception=e)

class CertValidator(DefaultValidator):
    """
    """
    name = "cert"

    def __init__(self, privateKey=None, pw=None, valid=True, allowed_X509Name=None, disallowed_X509Name=None):
        from OpenSSL import crypto
        if privateKey is not None:
            key_str = privateKey
            start, _, _, error, encrypted, exception = CertValidator.parse_(data=privateKey)
            try:
                if error == -1:
                    FileValidator().validate(privateKey)
                    with open(privateKey) as f:
                        key_str = "".join(f.readlines())
                    start, _, _, error, encrypted, exception = CertValidator.parse_(data=key_str)
                    if start is None:
                        raise InitException("path \"{path}\" contains no valid data.".format(path=privateKey))
                if error == -2:
                    raise InitException("can not load key: base64 encoding error", exception=exception)
                elif error < -2:
                    raise InitException("can not load key: see error log", exception=exception)
                if pw is None:
                    if encrypted:
                        raise InitException("Key is encrypted but no password is given")
                    self.m_pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key_str)
                else:
                    if not isinstance(pw, string_types):
                        raise InitException("Key pw must be an string")
                    self.m_pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key_str, str.encode(pw))
            except InitException:
                raise
            except Exception as e:
                logger.exception("can not load key")
                raise InitException("can not load key: {msg}".format(msg=CertValidator.get_exception_msg(e)), exception=e)
        else:
            self.m_pkey = None
        self.valid = valid is True
        self.allowed_X509Name = CertValidator.norm_X509Name(allowed_X509Name, start={}) if allowed_X509Name is not None else None
        self.disallowed_X509Name = CertValidator.norm_X509Name(disallowed_X509Name)

    @staticmethod
    def parse_(data, ends="PRIVATE KEY"):
        if "-----" in data:
            data_split = data.split("-----")
            if len(data_split) > 3:
                try:
                    assert data_split[1].rstrip(u'\r\n').strip().upper().startswith("BEGIN ")
                    assert data_split[1].rstrip(u'\r\n').strip().upper().endswith(" {ends}".format(ends=ends).upper())
                    assert data_split[3].rstrip(u'\r\n').strip().upper().startswith("END ")
                    assert data_split[3].rstrip(u'\r\n').strip().upper().endswith(" {ends}".format(ends=ends).upper())
                    from collections import defaultdict
                    pem_infos = {}
                    count = 0
                    for item in data_split[2].split('\n'):
                        if count not in pem_infos:
                            pem_infos[count] = ""
                        if item.rstrip(u'\r\n').strip() == "":
                            count += 1
                            continue
                        j = [pem_infos[count]]
                        j.append(item)
                        pem_infos[count] = u'\r\n'.join(j)
                    last = len(pem_infos.keys()) - 1 
                    logger.debug("check if cert contains valid Base64 data.")
                    Base64Validator(encoding=None).validate(pem_infos[last].strip())
                    encrypted = "ENCRYPTED" in data_split[1].rstrip(u'\r\n').strip().upper()
                    if last > 0:
                        res = ""
                        for idx in range(0, last):
                            res += pem_infos[idx]
                        encrypted = encrypted or "ENCRYPTED" in res.upper()
                    return (data_split[1].rstrip(u'\r\n').strip().upper(),
                            data_split[2].rstrip(u'\r\n').strip(),
                            data_split[3].rstrip(u'\r\n').strip().upper(),
                            0,
                            encrypted,
                            None)
                except ValidatorException as e:
                    # base65 validator fails
                    logger.error("certificate contained no valid Base64 data.")
                    return (None, None, None, -2, False, e)
                except Exception as e:
                    logger.exception("parsing error")
                    return (None, None, None, -3, False, e)
        # no vailed data
        logger.error("can not parse certificate data.")
        return (None, None, None, -1, False, None)
    
    @staticmethod
    def get_exception_msg(exception):
        msg = str(exception)
        if isinstance(exception, Exception) and hasattr(exception, "message"):
            if not exception.message:
                msg = ""
        if msg == "":
            return "Unknown Error"
        else:
            return msg

    @staticmethod
    def norm_X509Name(val_in, start=None):
        if start is None:
            res = dict(C=[], ST=[], L=[], O=[], OU=[], CN=[], emailAddress=[])
        else:
            assert isinstance(start, dict)
            res = start
        if val_in is None:
            return res
        assert isinstance(val_in, dict)
        mapping = dict(
            C="C", ST="ST", L="L", O="O", OU="OU", CN="CN", emailAddress="emailAddress",
            countryName="C", stateOrProvinceName="ST", localityName="L",
            organizationName="O", organizationalUnitName="OU", commonName="CN")
        for key, item in val_in.items():
            if key not in mapping:
                raise ParserException("invalid X509Name key: {key}".format(key=key))
            key = mapping[key]
            if key not in res:
                res[key] = []
            res[key].append(item)
            assert isinstance(item, string_types)
        return res

    def _get_str(self, value):
        if not isinstance(value, string_types):
            return str(value, "utf-8")
        return value

    def validate(self, value):
        from OpenSSL import crypto
        if not value.rstrip(u'\r\n').strip().startswith("-----BEGIN CERTIFICATE-----"):
            FileValidator().validate(value)
            with open(value) as f:
                value = "".join(f.readlines())
        try:
            cert_pub = crypto.load_certificate(crypto.FILETYPE_PEM, value)
        except Exception as e:
            raise ValidatorException("can not load certificate: {msg}".format(msg=CertValidator.get_exception_msg(e)), exception=e)
        if self.m_pkey is not None:
            try:
                tmp_data = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(50))
                signature = crypto.sign(self.m_pkey, tmp_data, "SHA1")
                crypto.verify(cert_pub, signature, tmp_data, "SHA1")
            except crypto.Error as e:
                raise ValidatorException("cert <-> key mismatch")
        if self.valid is True:
            utc_now = datetime.datetime.utcnow().replace(tzinfo=TZ())
            gtv = GeneralizedTimeValidator()
            not_after = gtv.validate(self._get_str(cert_pub.get_notAfter()))
            not_before = gtv.validate(self._get_str(cert_pub.get_notBefore()))
            if utc_now < not_before:
                raise ValidatorException(
                    "the certificate is valid not before {before}.".format(before=not_before))
            if utc_now > not_after:
                raise ValidatorException(
                    "the certificate is valid not after {after}.".format(after=not_after))
        sub = cert_pub.get_subject()
        errors = []
        for (key, value) in sub.get_components():
            key = self._get_str(key)
            value = self._get_str(value)
            if key in self.disallowed_X509Name and value in self.disallowed_X509Name[key]:
                errors.append("The value {value} is disallowed for {key}: {allowed}".format(
                    value=value, key=key, allowed=self.disallowed_X509Name[key]))
            if self.allowed_X509Name is not None:
                if key in self.allowed_X509Name and value not in self.allowed_X509Name[key]:
                    errors.append("The value {value} is not in the allowed values for {key}: {allowed}".format(
                        value=value, key=key, allowed=self.allowed_X509Name[key]))
        if len(errors) > 0:
            raise ValidatorException.from_list(errors)
        return value


class ItemsValidator(DefaultValidator):
    """
    """
    name = "items"

    def __init__(self, values=None, split_char=",", strip=True, min=None, max=None, skip_empty=False):
        self._values = values
        assert isinstance(self._values, list) or self._values is None
        self._split_char = split_char
        self._strip = strip
        self._min = min
        if min is not None:
            self._min = IntValidator().transform(min)
        self._max = max
        if self._max is not None:
            self._max = IntValidator().transform(max)
        self.skip_empty = skip_empty is True

    def validate(self, value):
        items = []
        for item in [value] if self._split_char is None else value.split(self._split_char):
            if self._strip:
                elm = item.strip()
            else:
                elm = item
            if self._values is not None:
                if elm not in self._values:
                    raise ValidatorException("Element '{elm}' ist not allowed: {allowed}".format(elm=elm, allowed=self._values))
            if elm not in items:
                if elm == "" and self.skip_empty is True:
                    continue
                items.append(elm)
        if self._min is not None:
            if len(items) < self._min:
                raise ValidatorException("the allowed number ({allowed}) was not reached ({entries}).".format(allowed=self._min, entries=len(items)))
        if self._max is not None:
            if len(items) > self._max:
                raise ValidatorException("the allowed number ({allowed}) has been exceeded ({entries}).".format(allowed=self._max, entries=len(items)))
        return items


class ItemValidator(ItemsValidator):
    """
    """
    name = "item"

    def __init__(self, values=None, strip=True):
        super(
            ItemValidator,
            self).__init__(
            values=values,
            split_char=None,
            strip=strip,
            min=1,
            max=1)

    def validate(self, value):
        items = super(ItemValidator, self).validate(value)
        return items[0]


class ListValidator(Validator):
    """
    """
    name = "list"

    def __init__(self, strict=False):
        self.strict = strict is True

    def validate(self, value):
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1]
        else:
            if self.strict:
                raise ValidatorException("input list elements with [...]")
        res = []
        for item_org in value.split(","):
            item = item_org.strip()
            if item.startswith("\"") and item.endswith("\"") or item.startswith("'") and item.endswith("'"):
                res.append(item[1:-1])
            else:
                if self.strict:
                    raise ValidatorException("items must be surrounded by \" or '")
                else:
                    if value.count(",") == 0 and item == "":
                        # listen der form []; [   ], ... (ohne inhalt) nicht in [""] umwandeln sondern in []
                        continue
                    res.append(item_org)
        return res


class DictValidator(Validator):
    """
    """
    name = "dict"

    def __init__(self, strict=False, duplicate_keys=False):
        self.strict = strict is True
        self.duplicate_keys = duplicate_keys is True
        # match key and value
        self.__key1 = re.compile(r"\s*(\"|')(?P<key>[^\1]*)\1{1}\s*(?P<rest>.*)")
        self.__key2 = re.compile(r"(?P<key>[^:]*)(?P<rest>.*)")
        self.__val1 = re.compile(r"\s*(\"|')(?P<value>[^\1]*)\1{1}\s*(?P<rest>.*)")
        self.__val2 = re.compile(r"\s*(?P<type>({|\[))\s*(?P<rest>.*)")
        self.__val3 = re.compile(r"(?P<value>[^,]*)(?P<rest>.*)")

    def validate(self, value):
        if value.startswith("{") and value.endswith("}"):
            value = value[1:-1]
        else:
            if self.strict:
                raise ValidatorException("input dict elements with {...}")
        res = {}
        item = value
        strict_error_msg = "items must be surrounded by \" or '"
        error_msq_split = "key and values must be split by :"
        while True:
            if item.strip() == "":
                break
            key1 = self.__key1.match(item)
            key2 = self.__key2.match(item)
            if key1 is not None:
                key = key1.group("key")
                item = key1.group("rest")
            elif key2 is not None:
                if self.strict:
                    raise ValidatorException(strict_error_msg)
                key = key2.group("key")
                item = key2.group("rest")
            else:
                raise ValidatorException("can not identify any dict key")
            if len(item) == 0 or item[0] != ":":
                raise ValidatorException(error_msq_split)
            item = item[1:]
            value1 = self.__val1.match(item)
            value2 = self.__val2.match(item)
            value3 = self.__val3.match(item)
            if value1 is not None:
                val = value1.group("value")
                item = value1.group("rest")
            elif value2 is not None:
                item, val = self._add_sub_item(value2.group("type"), value2.group("rest"))
            elif value3 is not None:
                if self.strict:
                    raise ValidatorException(strict_error_msg)
                val = value3.group("value")
                item = value3.group("rest")
            else:
                raise ValidatorException("can not identify any dict value")
            DictValidator.add_item(res, key, val, self.duplicate_keys)
            if len(item) > 0:
                if item[0] != ",":
                    raise ValidatorException("Key-value pairs must be split by comma.")
                item = item[1:]
        return res

    @staticmethod
    def add_item(d, key, value, duplicate_keys):
        assert isinstance(d, dict)
        if key in d:
            msg = "duplicate key input: {key}".format(key=key)
            if duplicate_keys is False:
                raise ValidatorException(msg)
            else:
                logger.warning(msg)
        d[key] = value
        
    @staticmethod
    def _find_relevant_sub_string(sub_type, item):
        revers = {"{": "}", "[": "]"}
        idx = 0
        count = 1
        for elm in item:
            idx += 1
            if elm == sub_type:
                count += 1
            elif elm == revers[sub_type]:
                count -= 1
            if count == 0:
                break
        if count != 0:
            raise ValidatorException("opening brace but no closing")
        return item[0: idx], item[idx+1:]
        
    def _add_sub_item(self, sub_type, item):
        relevant, rest = DictValidator._find_relevant_sub_string(sub_type, item)
        if sub_type == "{":
            dv = DictValidator(strict=self.strict, duplicate_keys=self.duplicate_keys)
            res = dv.validate("{" + relevant)
        elif sub_type == "[":
            lv = ListValidator(strict=self.strict)
            res = lv.validate("[" + relevant)
        else:
            raise ValidatorException("unsupported type: {type}".format(type=sub_type))
        return rest, res


class NetBIOSValidator(StringValidator):
    """
    """
    name = "netbios"

    def __init__(self):
        allowed_characters = list(string.ascii_uppercase + string.digits + string.ascii_lowercase)
        allowed_characters.append("!")
        allowed_characters.append("@")
        allowed_characters.append("#")
        allowed_characters.append("$")
        allowed_characters.append("%")
        allowed_characters.append("^")
        allowed_characters.append("&")
        allowed_characters.append("(")
        allowed_characters.append(")")
        allowed_characters.append("-")
        allowed_characters.append("_")
        allowed_characters.append("'")
        allowed_characters.append("{")
        allowed_characters.append("}")
        allowed_characters.append(".")
        allowed_characters.append("~")
        first_characters = list(allowed_characters)
        first_characters.remove(".")
        super(NetBIOSValidator, self).__init__(min_length=1, max_length=15, characters=allowed_characters, first=first_characters)

    def _validate_length(self, value, error_msg=None):
        return super(NetBIOSValidator, self)._validate_length(value, error_msg=" NetBIOS Name length")
    

class StripQuotationMark(DefaultValidator):
    
    def __init__(self, validator_name, allowed_quotation_mark_map=None, validator_parameter_dict=None, force_strip=False, output_quotation_mark=False):
        from configvalidator import load_validator
        validator_class = load_validator(validator_name)
        if validator_parameter_dict is None:
            validator_parameter_dict = {}
        assert isinstance(validator_parameter_dict, dict)
        self._validator = validator_class(**validator_parameter_dict)
        if allowed_quotation_mark_map is None:
            allowed_quotation_mark_map = [
                ("\"", "\""),
                ("'", "'"),
                (u"„", u"“"),
                (u"‚", u"‘"),
                (u"»", u"«"),
                (u"›", u"‹")
            ]
        assert isinstance(allowed_quotation_mark_map, list)
        self._allowed_quotation_mark_map = allowed_quotation_mark_map
        self._force_strip = force_strip is True
        self._output_quotation_mark = output_quotation_mark is True
        
    def validate(self, value):
        res = self.strip_quotation_mark(value)
        if self._output_quotation_mark is True and res != value:
            return value
        else:
            return res
    
    def strip_quotation_mark(self, value):
        errors = []
        val_exc = False
        if not self._force_strip:
            try:
                return self._validator.validate(value)
            except ValidatorException as e:
                val_exc = True
                errors.append(e)
            except Exception as e:
                errors.append(ValidatorException("Unknown Error", e))
        if len(value) < 2:
            errors.append(ValidatorException("can not strip quotation mark - input len must be at least 2!"))
        else:
            try:
                q_m_input = (value[0], value[-1])
                res = self._validator.validate(value[1:-1])
                if q_m_input not in self._allowed_quotation_mark_map:
                    errors.append(ValidatorException("The characters {input} are not in the list of allowed quotation mark.".format(input=q_m_input)))
                return res
            except ValidatorException as e:
                if not val_exc:
                    errors.append(e)
            except Exception as e:
                errors.append(ValidatorException("Unknown Error", e))
        raise ValidatorException.from_list(errors)

"""
generate classes that allowed Quotation Marks around inputs
"""
def generate_init_mepthod(elm):
    def __init__(self, **kwargs):
        StripQuotationMark.__init__(self,
                validator_name=elm.name,
                allowed_quotation_mark_map=[("'", "'"), ('"', '"')],
                validator_parameter_dict=kwargs,
                force_strip=False,
                output_quotation_mark=True)
    return __init__

for class_name, elm in [("StripQuotationMarkPathValidator", PathValidator),
                        ("StripQuotationMarkFileValidator", FileValidator),
                        ("StripQuotationMarkDirValidator", DirValidator)]:
    clazz = type(class_name, (StripQuotationMark,), {"__init__": generate_init_mepthod(elm), "name": "strip_" + elm.name})
    globals()[clazz.__name__] = clazz
    del clazz


class PortInUseValidator(PortValidator):
    name = "freePort"

    def __init__(self):
        super(PortInUseValidator, self).__init__(allow_null=False)

    def validate(self, value):
        port = super(PortInUseValidator, self).validate(value)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex(('127.0.0.1',port)) != 0:
            return port
        else:
            raise ValidatorException("Port {port} is not Free.".format(port=port))
