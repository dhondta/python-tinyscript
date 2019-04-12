#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Timing module assets' tests.

"""
from tinyscript.timing import set_time_items

from utils import *


args.stats = True
args.timings = True
set_time_items(globals())


class TestTiming(TestCase):
    def test_time_manager(self):
        self.assertFalse(time_manager.stats())
    
    def test_timer_object(self):
        with Timer() as timer:
            self.assertFalse(timer.fail)
            self.assertIs(timer.id, 0)
            self.assertTrue(timer.descr)
            self.assertTrue(timer.message)
            self.assertTrue(timer.start)
            self.assertFalse(timer.timeout)
    
    def test_timing_functions(self):
        self.assertFalse(get_time())
        self.assertFalse(get_time_since_last())
