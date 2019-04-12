#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common help utility help functions' tests.

"""
from unittest import main, TestCase

from tinyscript.helpers.lambdas import *


class TestLambdas(TestCase):
    def setUp(self):
        pass
    
    def test_data_conversion(self):
        self.assertEqual(bin2int("1"), 1)
        self.assertEqual(int2bin(1), "00000001")
        self.assertEqual(bin2txt("1100001"), "a")
        self.assertEqual(txt2bin("a"), "01100001")
        self.assertEqual(bin2txt(txt2bin("test", 8), 8), "test")
        self.assertEqual(bin2txt(txt2bin("test", 7), 7), "test")
        self.assertNotEqual(bin2txt(txt2bin("test", 6), 6), "test")
    
    def test_type_check(self):
        self.assertTrue(is_int(1))
        self.assertFalse(is_int("a"))
        self.assertTrue(is_pos_int(10))
        self.assertFalse(is_pos_int(-10))
        self.assertTrue(is_lst([0]))
        self.assertTrue(is_lst((0, 1, 2)))
        self.assertFalse(is_lst("not_a_list"))
        self.assertTrue(is_str("test"))
        self.assertFalse(is_str(1))
        self.assertTrue(is_lambda(lambda x: x))
        self.assertFalse(is_lambda(True))
    
    def test_data_format(self):
        self.assertTrue(is_bin("01000111"))
        self.assertFalse(is_bin("0123"))
        self.assertTrue(is_hex("deadbeef"))
        self.assertTrue(is_hex("c0ffee"))
        self.assertFalse(is_hex("coffee"))
        self.assertFalse(is_hex("00a"))
    
    def test_option_format_check(self):
        self.assertTrue(is_long_opt("--test"))
        self.assertFalse(is_long_opt("-t"))
        self.assertTrue(is_short_opt("-t"))
        self.assertFalse(is_short_opt("--test"))


if __name__ == '__main__':
    main()
