#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Data utility functions' tests.

"""
from tinyscript.helpers.data.utils import *
from tinyscript.helpers.data.utils import PAD

from utils import TestCase


class TestHelpersDataUtils(TestCase):
    def test_common_utility_functions(self):
        BIN = "01010"
        STR = "test"
        HEX = "deadbeefc0f3b1ac00"
        bs = BitArray("01010101")
        self.assertEqual(bs.nbits, 8)
        self.assertEqual(bs.bin, "01010101")
        self.assertEqual(bs.hex, "55")
        self.assertEqual(pad(STR, "\x00"), STR + 4 * "\x00")
        self.assertEqual(pad(STR, ">\x00"), 4 * "\x00" + STR)
        self.assertEqual(unpad(pad(STR, "\x00"), "\x00"), STR)
        self.assertEqual(pad(BIN, "bit"), BIN + "100")
        self.assertEqual(unpad(pad(BIN, "bit"), "bit"), BIN)
        self.assertRaises(ValueError, pad, STR, "000")
        self.assertRaises(ValueError, pad, "0101", PAD[0])
        self.assertRaises(ValueError, unpad, "0101", PAD[0])
        self.assertRaises(ValueError, pad, "", None, -1)
        self.assertRaises(ValueError, unpad, "", None, -1)
        for padding in PAD:
            for l in range(5, 15):
                self.assertEqual(unpad(pad(STR, padding, l), padding, l), STR)
                self.assertEqual(unpad(pad(HEX, padding, l), padding, l), HEX)
                self.assertEqual(unpad(pad(HEX, padding, l, True), padding, l, True), HEX)
        self.assertEqual(entropy(STR), 1.5)
        self.assertEqual(entropy(STR), entropy(list(map(ord, STR))))
        self.assertRaises(TypeError, entropy, 1)
        self.assertRaises(TypeError, entropy, pad)
        self.assertEqual(entropy_bits(STR), 19)
        self.assertRaises(TypeError, entropy_bits, 1)
        self.assertRaises(TypeError, entropy_bits, pad)
        self.assertEqual(entropy_bits("This is a test !"), 103)

