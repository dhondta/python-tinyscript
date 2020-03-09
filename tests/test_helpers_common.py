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
        self.assertEqual(list(bruteforce_mask("ab?l", {'l': "cde"})),
                         ["abc", "abd", "abe"])
        self.assertEqual(xor("this is a test", " "), "THIS\x00IS\x00A\x00TEST")
        self.assertEqual(list(strings("this is a \x00 test")),
                         ["this is a ", " test"])
        FILE, CONTENT = ".test_strings", b"this is a \x00 test"
        with open(FILE, 'wb') as f:
            f.write(CONTENT)
        self.assertIsNone(xor_file(FILE, " "))
        self.assertIsNone(xor_file(FILE, " "))
        with open(FILE, 'rb') as f:
            self.assertEqual(f.read(), CONTENT)
        self.assertEqual(list(strings_from_file(FILE)),
                         ["this is a ", " test"])
        remove(FILE)
