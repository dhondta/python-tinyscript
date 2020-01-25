#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Compatibility functions' tests.

"""
from tinyscript.helpers.common import *

from utils import remove, TestCase


class TestHelpersCommon(TestCase):
    def test_common_utility_functions(self):
        self.assertEqual(list(bruteforce(2, "ab")),
                         ["a", "b", "aa", "ab", "ba", "bb"])
        self.assertEqual(list(bruteforce(2, "ab", repeat=False)),
                         ["a", "b", "ab", "ba"])
        self.assertEqual(xor("this is a test", " "), "THIS\x00IS\x00A\x00TEST")
        self.assertIsNotNone(execute("id"))
        self.assertEqual(list(strings("this is a \x00 test")),
                         ["this is a ", " test"])
        FILE = ".test_strings"
        with open(FILE, 'wb') as f:
            f.write(b"this is a \x00 test")
        self.assertEqual(list(strings_from_file(FILE)),
                         ["this is a ", " test"])
        remove(FILE)
