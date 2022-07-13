#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Deprecation warning functions' tests.

"""
from unittest import main, TestCase

from tinyscript.deprecation import *
from tinyscript.deprecation import __features__


class TestDeprecation(TestCase):
    def test_deprecation_warnings(self):
        for f in __features__:
            self.assertRaises(DeprecationWarning, eval(f))

