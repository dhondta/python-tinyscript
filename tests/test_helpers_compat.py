#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Compatibility functions' tests.

"""
from tinyscript.helpers.compat import *

from utils import remove, TestCase


class TestHelpersCompat(TestCase):
    def test_compatibility_functions(self):
        CMD_PY = "print('hello')"
        TEST_PY = "execfile-test.py"
        with open(TEST_PY, 'w') as f:
            f.write(CMD_PY)
        execfile(TEST_PY)
        remove(TEST_PY)
