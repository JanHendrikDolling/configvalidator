# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""
import datetime
import math


class TZ(datetime.tzinfo):

    """
    universal datetime.tzinfo implementation
    """

    def __init__(self, hours=0, minutes=0):
        self._hours = hours
        self._minutes = minutes

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self._hours, minutes=self._minutes)

    def tzname(self, dt):
        if TZ.convert_timedelta(self.utcoffset(dt))> 0:
            return "UTC+{hours:02}:{minutes:02}".format(hours=TZ._p(self._hours), minutes=TZ._p(self._minutes))
        elif TZ.convert_timedelta(self.utcoffset(dt)) < 0:
            return "UTC-{hours:02}:{minutes:02}".format(hours=TZ._p(self._hours), minutes=TZ._p(self._minutes))
        else:
            return "UTC"

    def dst(self, dt):
        return self.utcoffset(dt)

    @staticmethod
    def convert_timedelta(timedelta):
        days, seconds = timedelta.days, timedelta.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)
        return days * 1440 + hours * 60 + minutes

    @staticmethod
    def _p(val):
        return int(math.fabs(val))
