# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest
from configvalidator.tools.timezone import TZ
import datetime


class MyTestCase(unittest.TestCase):

    def test_tzinfo_utc(self):
        self.assertEqual("UTC", TZ().tzname(None))
        self.assertEqual(datetime.timedelta(0), TZ().utcoffset(None))
        self.assertEqual(datetime.timedelta(0), TZ().dst(None))
        #
        self.assertEqual(datetime.timedelta(hours=-10), TZ(hours=-10).utcoffset(None))
        self.assertEqual(datetime.timedelta(minutes=1), TZ(minutes=1).dst(None))
        self.assertEqual(datetime.timedelta(minutes=-1), TZ(minutes=-1).dst(None))
        #
        self.assertEqual("UTC-02:39", TZ(hours=-2, minutes=-39).tzname(None))
        self.assertEqual("UTC-02:39", TZ(hours=-2, minutes=39).tzname(None))
        #
        self.assertEqual("UTC+00:39", TZ(minutes=39).tzname(None))
        self.assertEqual("UTC+22:04", TZ(hours=22, minutes=4).tzname(None))


if __name__ == '__main__':
    unittest.main()
