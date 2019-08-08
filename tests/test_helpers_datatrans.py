#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common utility lambdas' tests.

"""
from unittest import TestCase

from tinyscript.helpers.datatrans import *


class TestHelpersLambdas(TestCase):
    def setUp(self):
        global BIN, BIN_BE1, BIN_BE2, HEX, INT, STR
        BIN = "01110100011001010111001101110100"
        BIN_BE1 = "01110100011100110110010101110100"
        BIN_BE2 = "01100101011101000111010001110011"
        HEX = "74657374"
        INT = 0x74657374
        STR = "test"

    def test_data_conversion_from_bin(self):
        # bin -> hex
        self.assertEqual(bin2hex(BIN), HEX)
        self.assertEqual(bin2hex(BIN, 2, 3), HEX)
        self.assertRaises(ValueError, bin2hex, HEX)
        self.assertRaises(ValueError, bin2hex, INT)
        self.assertRaises(ValueError, bin2hex, STR)
        self.assertRaises(ValueError, bin2hex, BIN, -1)
        self.assertRaises(ValueError, bin2hex, BIN, 4, -1)
        self.assertRaises(ValueError, bin2hex, BIN, 8, 1, "", "bad_order")
        self.assertRaises(ValueError, bin2hex, "000 01", 2, 1, " ")
        # bin -> int
        self.assertEqual(bin2int(BIN), INT)
        self.assertEqual(bin2int(BIN, 2, 3), INT)
        self.assertRaises(ValueError, bin2int, HEX)
        self.assertRaises(ValueError, bin2int, INT)
        self.assertRaises(ValueError, bin2int, STR)
        self.assertRaises(ValueError, bin2int, BIN, -1)
        self.assertRaises(ValueError, bin2int, BIN, 4, -1)
        self.assertRaises(ValueError, bin2int, BIN, 8, 1, "", "bad_order")
        self.assertRaises(ValueError, bin2int, "000 01", 2, 1, " ")
        # bin -> str
        self.assertEqual(bin2str(BIN), STR)
        self.assertEqual(bin2str(BIN, 2, 3), STR)
        self.assertRaises(ValueError, bin2str, HEX)
        self.assertRaises(ValueError, bin2str, INT)
        self.assertRaises(ValueError, bin2str, STR)
        self.assertRaises(ValueError, bin2str, BIN, -1)
        self.assertRaises(ValueError, bin2str, BIN, 4, -1)
        self.assertRaises(ValueError, bin2str, BIN, 8, 1, "", "bad_order")
        self.assertRaises(ValueError, bin2str, "000 01", 2, 1, " ")

    def test_data_conversion_from_hex(self):
        # hex -> bin
        self.assertEqual(hex2bin(HEX), BIN)
        self.assertRaises(ValueError, hex2bin, INT)
        self.assertRaises(ValueError, hex2bin, STR)
        self.assertRaises(ValueError, hex2bin, HEX, -1)
        self.assertRaises(ValueError, hex2bin, HEX, 4, -1)
        self.assertRaises(ValueError, hex2bin, HEX, 8, 1, "", "bad_order")
        # hex -> int
        self.assertEqual(hex2int(HEX), INT)
        self.assertRaises(ValueError, hex2int, INT)
        self.assertRaises(ValueError, hex2int, STR)
        # hex -> str
        self.assertEqual(hex2str(HEX), STR)
        self.assertRaises(ValueError, hex2str, INT)
        self.assertRaises(ValueError, hex2str, STR)

    def test_data_conversion_from_int(self):
        # int -> bin
        self.assertEqual(int2bin(INT), BIN)
        self.assertEqual(int2bin(INT, order="big"), BIN_BE1)
        self.assertEqual(int2bin(INT, 8, 5), "0" * 8 + BIN)
        self.assertEqual(int2bin(INT, 8, 2, order="big"), BIN_BE2)
        self.assertRaises(ValueError, int2bin, BIN)
        self.assertRaises(ValueError, int2bin, HEX)
        self.assertRaises(ValueError, int2bin, STR)
        self.assertRaises(ValueError, int2bin, INT, -1)
        self.assertRaises(ValueError, int2bin, INT, 4, -1)
        self.assertRaises(ValueError, int2bin, INT, 8, 1, "", "bad_order")
        # int -> hex
        self.assertEqual(int2hex(INT), HEX)
        self.assertEqual(int2hex(INT, len(HEX) // 2 + 1), "00" + HEX)
        self.assertRaises(ValueError, int2hex, BIN)
        self.assertRaises(ValueError, int2hex, HEX)
        self.assertRaises(ValueError, int2hex, STR)
        self.assertRaises(ValueError, int2hex, INT, 0)
        # int -> str
        self.assertEqual(int2str(INT), STR)
        self.assertEqual(int2str(29797, 29556), STR)
        self.assertRaises(ValueError, int2hex, BIN)
        self.assertRaises(ValueError, int2hex, HEX)
        self.assertRaises(ValueError, int2hex, STR)

    def test_data_conversion_from_str(self):
        # str -> bin
        self.assertEqual(str2bin(STR), BIN)
        self.assertRaises(ValueError, str2bin, INT)
        self.assertRaises(ValueError, str2bin, STR, -1)
        self.assertRaises(ValueError, str2bin, STR, 4, -1)
        self.assertRaises(ValueError, str2bin, STR, 8, 1, "", "bad_order")
        # str -> hex
        self.assertEqual(str2hex(STR), HEX)
        self.assertRaises(ValueError, str2hex, INT)
        # str -> int
        self.assertEqual(str2int(STR), INT)
        self.assertRaises(ValueError, str2int, INT)
        self.assertRaises(ValueError, str2int, STR, -1)
