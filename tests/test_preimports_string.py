#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports string assets' tests.

"""
from tinyscript.preimports import string

from utils import *


class TestPreimportsString(TestCase):
    def test_extra_string_functions(self):
        STR = "this is a test"
        self.assertEqual(string.shorten("test"), "test")
        self.assertTrue(len(string.shorten(100 * STR)) < len(100 * STR))
        self.assertTrue(string.shorten(100 * STR).endswith("..."))
        self.assertTrue(string.shorten(100 * STR, end="|||").endswith("|||"))
        self.assertRaises(ValueError, string.shorten, "test", "BAD_LENGTH")
        LST = ["base1", "base2", "base10", "base30", "base200"]
        l = sorted(LST)
        string.sort_natural(l)
        self.assertEqual(tuple(LST), tuple(l))
        self.assertEqual(tuple(LST), tuple(string.sorted_natural(l)))

