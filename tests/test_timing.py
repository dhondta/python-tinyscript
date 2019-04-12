#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Timing module assets' tests.

"""
import time

from tinyscript.timing import set_time_items

from utils import *


args.stats = True
args.timings = True
set_time_items(globals())


class TestTiming(TestCase):
    def test_step_setup(self):
        g = globals().keys()
        self.assertTrue(args.stats)
        self.assertTrue(args.timings)
        self.assertIn("get_time", g)
        self.assertIn("get_time_since_last", g)
        self.assertIn("Timer", g)

    def test_time_manager(self):
        self.assertFalse(time_manager.stats())
    
    def test_timer_object(self):
        temp_stdout(self)
        with Timer() as timer:
            self.assertFalse(timer.fail)
            self.assertIs(timer.id, 0)
            self.assertTrue(timer.descr)
            self.assertTrue(timer.message)
            self.assertTrue(timer.start)
            self.assertFalse(timer.timeout)
            self.assertRaises(Timer.TimeoutError, timer._handler, None, None)
        
        def timeout_test():
            with Timer(timeout=1) as t:
                time.sleep(2)

        self.assertRaises(Timer.TimeoutError, timeout_test)
    
    def test_timing_functions(self):
        temp_stdout(self)
        self.assertFalse(get_time())
        self.assertFalse(get_time("test"))
        self.assertFalse(get_time_since_last())
        self.assertFalse(get_time_since_last("test"))