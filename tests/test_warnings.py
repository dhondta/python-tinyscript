#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common custom type validations' tests.

"""
from unittest import main, TestCase

from tinyscript.warnings import *
from tinyscript.warnings import __features__


class TestWarnings(TestCase):
    def test_deprecation_warnings(self):
        for f in __features__:
            self.assertRaises(DeprecationWarning, eval(f))

