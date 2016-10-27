# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os
import pep8
import inspect
import six
try:
    import configvalidator
except ImportError:
    import sys
    sys.path.append(os.getcwd())
    import configvalidator

LINE_TOO_LONG = False
configValidator_base = os.path.dirname(inspect.getfile(configvalidator))
configValidator_test_base = os.path.dirname(__file__)


class TestMeta(type):

    def __new__(mcs, name=None, bases=None, dict=None):
        if name is None:  # fix for pypy
            return None
        files = []
        for directory, _, filenames in os.walk(configValidator_base):
            if directory.endswith(os.path.sep + "__pycache__"):
                continue
            for f in filenames:
                if f.endswith(".py"):
                    files.append(
                        (configValidator_base, os.path.join(directory, f)))
        for directory, _, filenames in os.walk(configValidator_test_base):
            for f in filenames:
                if f.endswith(".py"):
                    files.append((
                        configValidator_test_base,
                        os.path.join(directory, f)
                    ))
            break
        for base, item in files:
            test_method_name = item[len(base) + 1:-3]
            test_method_name = test_method_name.replace(os.path.sep, "_")
            test_method_name = test_method_name.replace(" ", "_")
            test_method_name = "test_pep8_file_{name}".format(
                name=test_method_name)
            check_name = "{name}".format(name=item)
            dict[test_method_name] = TestMeta.make_test_fn(item)
        return type.__new__(mcs, name, bases, dict)

    @staticmethod
    def make_test_fn(file_path):
        def f(self):
            self._pep8_check(file_path)
        return f


@six.add_metaclass(TestMeta)
class TestCodeFormat(unittest.TestCase):

    def _pep8_check(self, file_path):
        # print(file_path)
        pep8style = pep8.StyleGuide(quiet=True)
        result = pep8style.check_files([file_path])
        max_error = 0
        if LINE_TOO_LONG is False and "E501" in result.counters:
            max_error = result.counters["E501"]
            if "E402" in result.counters:
                max_error += result.counters["E402"]
        self.assertEqual(
            result.total_errors,
            max_error,
            "Found code style errors in {file} (and warnings):\n{res}".format(file=file_path,
                                                                              res="\n".join(result.get_statistics()))
        )

if __name__ == "__main__":
    unittest.main()
