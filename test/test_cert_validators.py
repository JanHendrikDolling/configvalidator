# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""
import os
import sys
try:
    import mock
except ImportError:
    from unittest import mock
import re
import types
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from configvalidator import ValidatorException
from configvalidator import ParserException, InitException
import testutils


PYPY3 = hasattr(sys, 'pypy_version_info') and sys.version_info.major >= 3

class Test(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(testutils.get_test_utils_base(), "certs", "not_before", "key"), "r") as f:
            self.not_before_key = f.read()
        with open(os.path.join(testutils.get_test_utils_base(), "certs", "not_before", "cert"), "r") as f:
            self.not_before_cert = f.read()

    @unittest.skipIf(PYPY3, "...")
    def test_cert(self):
        not_before_key = self.not_before_key
        not_before_cert = self.not_before_cert
        from configvalidator.validators import CertValidator
        # normal
        v1 = CertValidator(
            privateKey=os.path.join(
                testutils.get_test_utils_base(),
                "data",
                "exist",
                "certs",
                "key_1.pem"))
        v1.validate(
            os.path.join(
                testutils.get_test_utils_base(),
                "data",
                "exist",
                "certs",
                "cert_1.crt"))
        with self.assertRaises(ValidatorException) as e1:
            v1.validate(
                os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "certs",
                    "cert_2.crt"))
        self.assertEqual(str(e1.exception), 'cert <-> key mismatch')
        with self.assertRaises(ValidatorException) as e2:
            v1.validate(
                os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "not_exist",
                    "certs",
                    "cert_3.crt"))
        self.assertEqual(str(e2.exception), "path \"{testutils}\" doesn't exist".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "not_exist", "certs", "cert_3.crt")))
        # crypt
        v2 = CertValidator(
            privateKey=os.path.join(
                testutils.get_test_utils_base(),
                "data",
                "exist",
                "certs",
                "key_2_crypt.pem"),
            pw="123456")
        v2.validate(
            os.path.join(
                testutils.get_test_utils_base(),
                "data",
                "exist",
                "certs",
                "cert_2.crt"))
        with self.assertRaises(ValidatorException) as e3:
            v2.validate(
                os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "certs",
                    "cert_1.crt"))
        self.assertEqual(str(e3.exception), 'cert <-> key mismatch')
        # no key
        with self.assertRaises(InitException) as e4:
            CertValidator(
                privateKey=os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "certs",
                    "key_2_crypt.pem"))
        self.assertEqual(
            str(e4.exception),
            "Key is encrypted but no password is given")
        # not valid (before)
        v3 = CertValidator(privateKey=not_before_key)
        with self.assertRaises(ValidatorException) as e5:
            v3.validate(value=not_before_cert)
        self.assertEqual(
            str(e5.exception),
            "the certificate is valid not before 2115-05-21 11:02:17+00:00.")
        # not valid (before) <-> not validation
        v4 = CertValidator(valid=False)
        v4.validate(value=not_before_cert)
        # not valid (after)
        v5 = CertValidator(
            privateKey=os.path.join(
                testutils.get_test_utils_base(),
                "data",
                "exist",
                "certs",
                "key_3.pem"))
        with self.assertRaises(ValidatorException) as e6:
            v5.validate(
                value=os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "certs",
                    "cert_3.crt"))
        self.assertEqual(
            str(e6.exception),
            "the certificate is valid not after 2015-06-14 12:14:42+00:00.")
        # not valid (after) <-> not validation
        v6 = CertValidator(
            privateKey=os.path.join(
                testutils.get_test_utils_base(),
                "data",
                "exist",
                "certs",
                "key_3.pem"),
            valid=False)
        v6.validate(
            value=os.path.join(
                testutils.get_test_utils_base(),
                "data",
                "exist",
                "certs",
                "cert_3.crt"))
        v7 = CertValidator(valid=False)
        v7.validate(
            value=os.path.join(
                testutils.get_test_utils_base(),
                "data",
                "exist",
                "certs",
                "cert_3.crt"))
        v8 = CertValidator()
        with self.assertRaises(ValidatorException) as e7:
            v8.validate(
                value=os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "certs",
                    "cert_3.crt"))
        self.assertEqual(
            str(e7.exception),
            "the certificate is valid not after 2015-06-14 12:14:42+00:00.")
        # disallowed values
        v9 = CertValidator(disallowed_X509Name=dict(commonName="cn"))
        with self.assertRaises(ValidatorException) as e8:
            v9.validate(
                value=os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "certs",
                    "cert_1.crt"))
        self.assertEqual(
            str(e8.exception),
            "The value cn is disallowed for CN: ['cn']")
        v10 = CertValidator(disallowed_X509Name=dict(CN="cn"))
        with self.assertRaises(ValidatorException) as e9:
            v10.validate(
                value=os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "certs",
                    "cert_1.crt"))
        self.assertEqual(
            str(e9.exception),
            "The value cn is disallowed for CN: ['cn']")
        #
        v11 = CertValidator(allowed_X509Name=dict(CN="foo"))
        with self.assertRaises(ValidatorException) as e10:
            v11.validate(
                value=os.path.join(
                    testutils.get_test_utils_base(),
                    "data",
                    "exist",
                    "certs",
                    "cert_1.crt"))
        self.assertEqual(
            str(e10.exception),
            "The value cn is not in the allowed values for CN: ['foo']")

    def test_cert_1(self):
        from configvalidator.validators import CertValidator
        with self.assertRaises(InitException) as e1:
            CertValidator(privateKey=os.path.join(testutils.get_test_utils_base(), "data", "not_exist", "key.pem"))
        self.assertEqual("can not load key: path \"{testutils}\" doesn't exist".format(testutils=os.path.join(testutils.get_test_utils_base(), "data", "not_exist", "key.pem")), str(e1.exception))
        not_before_key_2 = """
-----BEGIN RSA PRIVATE KEY-----
12345
67890
1
-----END RSA PRIVATE KEY-----
"""
        with self.assertRaises(InitException) as e2:
            CertValidator(privateKey=not_before_key_2)
        self.assertEqual("can not load key: base64 encoding error", str(e2.exception))
        with self.assertRaises(InitException) as e3:
            CertValidator(privateKey=os.path.join(testutils.get_test_utils_base(), "data", "exist", "empty.ini"))
        self.assertEqual("path \"{path}\" contains no valid data.".format(path=os.path.join(testutils.get_test_utils_base(), "data", "exist", "empty.ini")), str(e3.exception))

    def test_cert_CertValidator(self):
        from configvalidator.validators import CertValidator

        class Exc(Exception):
            message = []
        res = CertValidator.get_exception_msg(Exc())
        self.assertEqual("Unknown Error", res)

    def test_cert_norm_X509Name(self):
        from configvalidator.validators import CertValidator
        in1 = dict(
            C="C_1",
            ST="ST_1",
            L="L_1",
            O="O_1",
            OU="OU_1",
            CN="CN_1",
            emailAddress="emailAddress_1",
        )
        res1 = CertValidator.norm_X509Name(val_in=in1)
        in2 = dict(
            emailAddress="emailAddress_1",
            countryName="C_1",
            stateOrProvinceName="ST_1",
            localityName="L_1",
            organizationName="O_1",
            organizationalUnitName="OU_1",
            commonName="CN_1",
        )
        res2 = CertValidator.norm_X509Name(val_in=in2)
        self.assertDictEqual(res1, res2)
        with self.assertRaises(ParserException) as e:
            CertValidator.norm_X509Name(val_in={"fooo": "bar"})
        self.assertEqual("invalid X509Name key: fooo", str(e.exception))

    @unittest.skipIf(PYPY3, "...")
    def test_cert_XXXXXXXXXXX(self):
        # FIXME anderen pricate KEY!!!!!!
        key = """
-----BEGIN PRIVATE KEY-----
Proc-Type: ENCRYPTED

MIICxzBBBgkqhkiG9w0BBQ0wNDAbBgkqhkiG9w0BBQwwDgQIEOK1z4orG5QCAggA
MBUGCSsGAQQBl1UBAgQIo8g5+FaUsaQEggKAS9/E3kXpI/gW88MCVsTYgwQEA0KC
bifNcytbPZmGSEe1xOhz3KX8N3BTlLZfATeRXxVwPF1v6Rsss0J+4FeVLSH+1NNc
L7mDB+gTSq09skYHeHCzAHDCZaCur0luMgoRqoFVZ6Eh8kIlkJZqHoXBX7Ndlglv
sHHho9GKWUjjqhOjBIJqHPG4u2o8sQbVNTvwX2swDgQ5HxrKrRspBBC82QdLL0J5
apHGu/ev+ArGvrttttDiDJtzIjresiUurG0J0V4ozf633cW2Fb3rKT6yng4f1NM5
k18nsCD4AH+aZm3yTsQNDdrDugqBt6hPaoP0Jyl799+8K/LX7hUgFy9f/gTTqTXM
8lw9fA5jVRV9runh6XvLgLy/xJXNknrnapSpRaw0EpDmzmB2y6WsRtGoJCK4mB1P
5bBhe3d7yMq0qL+l2GvUP0T5Dox763Pb0h78U9PAnijMtzeeEoeoPYLWj7bjTDQU
tJ/AHSsEfZ5jN0FM8nXCkDK+eeAGbXU9UsrJdKJaXz3yVg4qEo2dMii5dkZfEk5o
8BLjD6zHFkcd6tGUaKOp00X4NxRfD2ZlMYdT7K1AmePJkZ3BoH96QEf7gafpbbmm
iNZtaGvzcb2ZvUt5IXs/unbZklOUcBK1xXINRo4zL8IUPY6z/a5x+qU5V9qKJpHp
DudeioqqfAb/1Lr8Zjk0qm8VzJNEIEq7WuxVZvvGvmsp+ReeBEu1jDXOGl8G7qWf
qDC87meLLKGvm4TM26dzjIrOIojgyTJxISGO/trmRef9YUFUDcodfyPNAxJTLk3N
sSQ+pr1dDQrM/dvU5Wy/og8wrw7es5uxqmxbmYW/G/znxoC22HbWdgS2FQ==
-----END PRIVATE KEY-----
"""
        from configvalidator.validators import CertValidator
        with self.assertRaises(InitException) as e1:
            CertValidator(privateKey=key)
        self.assertTrue(str(e1.exception).startswith("Key is encrypted but no password is given"))

    @unittest.skipIf(PYPY3, "...")
    def test_cert_load(self):
        from configvalidator.validators import CertValidator
        with self.assertRaises(InitException) as e:
            CertValidator(privateKey="-----BEGIN PRIVATE KEY-----\n....")
        self.assertTrue(str(e.exception).startswith("can not load key: "))
        c = CertValidator()
        with self.assertRaises(ValidatorException) as e2:
            c.validate("-----BEGIN CERTIFICATE-----\n.....")
        self.assertTrue(str(e2.exception).startswith("can not load certificate: "))
        with self.assertRaises(InitException) as e3:
            CertValidator(
                privateKey=os.path.join(testutils.get_test_utils_base(), "data", "exist", "certs", "key_2_crypt.pem"),
                pw=object())
        self.assertEqual("Key pw must be an string", str(e3.exception))

    @unittest.skipIf(PYPY3, "mock error with pypy3 version 2.4")
    def test_CertValidator_error(self):
        key = self.not_before_key
        from configvalidator.validators import CertValidator
        from configvalidator.validators import Base64Validator
        # mock
        with mock.patch.object(Base64Validator, 'validate', side_effect=Exception('FAIL')) as mock_method:
            with self.assertRaises(InitException) as e:
                CertValidator(privateKey=key)
            self.assertEqual(1, len(e.exception.errors))
            error_msg, excp = e.exception.errors[0]
            self.assertEquals('can not load key: see error log', error_msg)
            self.assertEquals("FAIL", str(excp))
        # reset mock
        v = Base64Validator()
        self.assertEqual("Hallo Welt!", v.validate("SGFsbG8gV2VsdCE="))


if __name__ == '__main__':
    unittest.main()