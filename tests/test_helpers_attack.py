#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Attack helper functions' tests.

"""
from tinyscript.helpers.attack import *

from utils import remove, TestCase


class TestHelpersAttack(TestCase):
    def test_attack_functions(self):
        self.assertEqual(list(bruteforce(2, "ab")), ["a", "b", "aa", "ab", "ba", "bb"])
        self.assertEqual(list(bruteforce(2, "ab", repeat=False)), ["a", "b", "ab", "ba"])
        DICT = ".test-dictionary-attack.txt"
        with open(DICT, 'wt') as f:
            f.write("password\ntest")
        self.assertEqual(list(dictionary(DICT)), ['password', 'test'])
        self.assertEqual(list(dictionary(DICT, rules="i,sta[0]")), ['password', 'Password0', 'test', 'Test0'])
        remove(DICT)
    
    def test_mask_string_expansion(self):
        self.assertIsNotNone(expand_mask("???c?(abc)"))
        self.assertRaises(ValueError, expand_mask, "?(")
        self.assertRaises(ValueError, expand_mask, "?()")
        self.assertRaises(ValueError, expand_mask, "?(v()")
        self.assertIsNotNone(expand_mask("??(v()"))
        self.assertRaises(ValueError, expand_mask, "?z")
        self.assertEqual(expand_mask("?z", {'z': "xyz"}), ["xyz"])
        self.assertEqual(expand_mask("?v"), ["aeiouy"])
        self.assertEqual(expand_mask("?v", {'v': "abc"}), ["abc"])
        self.assertEqual(list(bruteforce_mask("ab?l", {'l': "cde"})), ["abc", "abd", "abe"])
        self.assertEqual(list(bruteforce_mask(["a", "b", "cde"])), ["abc", "abd", "abe"])
        g = bruteforce_mask(12345)
        self.assertIsNotNone(g)
        self.assertRaises(ValueError, list, g)
    
    def test_rule_parsing(self):
        self.assertTrue(list(parse_rule("icrstu")))
        self.assertTrue(list(parse_rule("p[TEST]a[123]")))
        for g in [parse_rule("rz"), parse_rule("z[test]"), parse_rule("p[test]]"), parse_rule("p[[test]")]:
            self.assertIsNotNone(g)
            self.assertRaises(ValueError, list, g)

