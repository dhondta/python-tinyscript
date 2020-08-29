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
        self.assertRaises(ValueError, list, bruteforce(-1))
        self.assertRaises(ValueError, list, bruteforce(2, minlen=-1))
        self.assertRaises(ValueError, list, bruteforce(1, minlen=3))
        DICT = ".test-dictionary-attack.txt"
        with open(DICT, 'wt') as f:
            f.write("password\ntest")
        self.assertEqual(list(dictionary(DICT)), ['password', 'test'])
        self.assertEqual(list(dictionary(DICT, rules="i,sta[0]")), ['password', 'Password0', 'test', 'Test0'])
        remove(DICT)
        self.assertEqual(sorted(list(bruteforce(3, "abc"))), sorted(list(bruteforce_re(r"[a-c]{1,3}"))))
        self.assertRaises(ValueError, list, bruteforce_re(1234))
        for i in range(1, 5):
            self.assertEqual(len(list(bruteforce_pin(i))), 10 ** i)
        self.assertRaises(ValueError, list, bruteforce_pin(0))
    
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

