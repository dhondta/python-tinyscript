#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Timing module assets' tests.

"""
import time

from tinyscript.features.timing import set_time_items
from tinyscript.helpers.timeout import TimeoutError

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
        with Timer() as t:
            pass
        self.assertFalse(time_manager.stats())
    
    def test_timer_object(self):
        if WINDOWS:
            logger.warning("Timeout-related features are not implemented for Windows")
        else:
            temp_stdout(self)
            with self.assertRaises(TimeoutError):
                with Timer(timeout=1, fail_on_timeout=True) as timer:
                    self.assertTrue(timer.fail)
                    self.assertTrue(timer.descr)
                    self.assertTrue(timer.message)
                    self.assertTrue(timer.start)
                    self.assertEqual(timer.timeout, 1)
                    self.assertRaises(TimeoutError, timer._handler, None, None)
                    time.sleep(2)
            with Timer(timeout=1):
                time.sleep(2)
    
    def test_timing_functions(self):
        temp_stdout(self)
        self.assertFalse(get_time())
        self.assertFalse(get_time("test"))
        self.assertFalse(get_time_since_last())
        self.assertFalse(get_time_since_last("test"))

