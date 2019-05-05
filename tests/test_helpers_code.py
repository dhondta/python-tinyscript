#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common utility help functions' tests.

"""
from unittest import TestCase

from tinyscript.helpers.code import *

from utils import *


class TestHelpersCode(TestCase):
    def test_function_replacement(self):
        temp_stdout(self)
        def dummy(): return 1
        self.assertEqual(dummy(), 1)
        code_replace(dummy, "def dummy(): return 1", "def dummy(): return 42")
        self.assertEqual(dummy(), 42)
        def dummy(): return 1
        code_replace(dummy, "return 1", "return 42")
        self.assertEqual(dummy(), 42)
        code_restore(dummy)
        self.assertEqual(dummy(), 1)
        def dummy(): return 1
        self.assertRaises(ValueError, code_replace, dummy, "bad")
