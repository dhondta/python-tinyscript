#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Timeout utility assets' tests.

"""
from tinyscript.helpers.timeout import timeout, Timeout, TimeoutError

from utils import *


class TestHelpersTimeout(TestCase):
    def test_timeout_execution(self):
        if WINDOWS:
            with self.assertRaises(NotImplementedError):
                timeout(1)(dummy_sleep)
        else:
            test = timeout(1)(dummy_sleep)
            self.assertIsNone(test())
            test = timeout(1, "", True)(dummy_sleep)
            self.assertRaises(TimeoutError, test)
            test = timeout(3)(dummy_sleep)
            self.assertEqual(test(), "TEST")

