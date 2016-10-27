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
import socket
import configvalidator
import random


class OpenSocket(object):

    def __init__(self, port):
        self.serversocket = None
        self.port = port
        try:
            #create an INET, STREAMing socket
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #bind the socket to a public host,
            # and a well-known port
            self.serversocket.bind(('127.0.0.1', self.port))
            #become a server socket
            self.serversocket.listen(5)
            self.stop_thread = False
        except OSError:
            self.port = None

    def stop(self):
        if self.serversocket is not None:
            self.serversocket.close()


class Test(unittest.TestCase):

    def test_port_free(self):
        from configvalidator.validators import PortInUseValidator
        while True:
            port = random.randint(2000, 65000)
            o = OpenSocket(port)
            if o.port is not None:
                o.stop()
                self.assertEqual(port, PortInUseValidator().validate("{port}".format(port=port)))
                break

    def test_(self):
        from configvalidator.validators import PortInUseValidator
        o = OpenSocket(8080)
        with self.assertRaises(configvalidator.ValidatorException) as e:
            PortInUseValidator().validate("8080")
        self.assertEqual("Port 8080 is not Free.", str(e.exception))
        o.stop()

