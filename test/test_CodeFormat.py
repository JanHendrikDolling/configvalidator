'''
Created on 30.04.2014

@author: zoidberg
'''
import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import pep8
import inspect
from configvalidator import ConfigValidator


class TestCodeFormat(unittest.TestCase):

    def test_pep8_conformance(self):
        """Test that we conform to PEP8."""
        path = inspect.getfile(ConfigValidator)
        if path.endswith(".pyc"):
            path = path[0:-3] + 'py'
        pep8style = pep8.StyleGuide(quiet=True)
        result = pep8style.check_files([path])
        self.assertEqual(
            result.total_errors,
            0,
            "Found code style errors (and warnings).")

    def test_pep8_conformance_init_file(self):
        """Test that we conform to PEP8."""
        path = os.path.join(os.path.dirname(inspect.getfile(ConfigValidator)), "__init__.py")
        pep8style = pep8.StyleGuide(quiet=True)
        result = pep8style.check_files([path])
        self.assertEqual(
            result.total_errors,
            0,
            "Found code style errors (and warnings).")

if __name__ == "__main__":
    unittest.main()
