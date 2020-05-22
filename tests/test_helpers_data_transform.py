#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Data transformation tests.

"""
from tinyscript.helpers.data.transform import *

from utils import TestCase


class TestHelpersDataTransform(TestCase):
    def setUp(self):
        global BIN, BIN_LE, HEX, INT, STR
        BIN = "01110100011001010111001101110100"
        BIN_LE = "01110100011100110110010101110100"
        HEX = "74657374"
        INT = 1952805748
        STR = "test"

    def test_data_conversion_from_bin(self):
        # bin -> bin
        self.assertEqual(bin2bin("100000"), "00100000")
        self.assertEqual(bin2bin(BIN), BIN)
        self.assertRaises(ValueError, bin2bin, HEX)
        self.assertRaises(ValueError, bin2bin, BIN, -1)
        self.assertRaises(ValueError, bin2bin, BIN, 8, -1)
        # bin -> hex
        self.assertEqual(bin2hex("100000"), "20")
        self.assertEqual(bin2hex(BIN), HEX)
        self.assertEqual(bin2hex(BIN, 2), "01030100010201010103000301030100")
        self.assertEqual(bin2hex(BIN, 8, 2), "1c")
        self.assertEqual(bin2hex(BIN, 8, 10), "1d0651cc74")
        self.assertRaises(ValueError, bin2hex, HEX)
        self.assertRaises(ValueError, bin2hex, INT)
        self.assertRaises(ValueError, bin2hex, STR)
        self.assertRaises(ValueError, bin2hex, BIN, -1)
        self.assertRaises(ValueError, bin2hex, BIN, 8, -1)
        # bin -> int
        self.assertEqual(bin2int("100000"), 32)
        self.assertEqual(bin2int(BIN), INT)
        self.assertEqual(bin2int(BIN, nbits_out=10), 124660075636)
        self.assertEqual(bin2int(BIN, nbits_out=2), 28)
        self.assertRaises(ValueError, bin2int, HEX)
        self.assertRaises(ValueError, bin2int, INT)
        self.assertRaises(ValueError, bin2int, STR)
        self.assertRaises(ValueError, bin2int, BIN, -1)
        self.assertRaises(ValueError, bin2int, BIN, 8, -1)
        self.assertRaises(ValueError, bin2int, BIN, 8, 8, "bad_order")
        self.assertEqual(bin2ints(BIN), [INT])
        self.assertEqual(bin2ints(BIN, n_chunks=2), [29797, 29556])
        self.assertEqual(bins2int(BIN[:16], BIN[16:]), INT)
        self.assertRaises(ValueError, bin2int, BIN, unsigned="bad")
        # bin -> str
        self.assertEqual(bin2str("100000"), " ")
        self.assertEqual(bin2str(str2lst("100000")), " ")
        self.assertEqual(bin2str(BIN), STR)
        self.assertEqual(bin2str(BIN, 2),
            "\x01\x03\x01\x00\x01\x02\x01\x01\x01\x03\x00\x03\x01\x03\x01\x00")
        self.assertRaises(ValueError, bin2str, HEX)
        self.assertRaises(ValueError, bin2str, INT)
        self.assertRaises(ValueError, bin2str, STR)
        self.assertRaises(ValueError, bin2str, BIN, -1)
        self.assertRaises(ValueError, bin2str, BIN, 8, -1)
        # * -> bins
        self.assertRaises(ValueError, int2bins, INT, n_chunks=-1)
        self.assertRaises(ValueError, str2bins, STR, len_in=-1)
        self.assertRaises(ValueError, hex2bins, BIN, len_out=-1)

    def test_data_conversion_from_hex(self):
        # hex -> bin
        self.assertEqual(hex2bin(HEX), BIN)
        self.assertRaises(ValueError, hex2bin, INT)
        self.assertRaises(ValueError, hex2bin, STR)
        self.assertRaises(ValueError, hex2bin, HEX, -1)
        self.assertRaises(ValueError, hex2bin, HEX, 8, -1)
        # hex -> int
        self.assertEqual(hex2int(HEX), INT)
        self.assertRaises(ValueError, hex2int, INT)
        self.assertRaises(ValueError, hex2int, STR)
        # hex -> str
        self.assertEqual(hex2str(HEX), STR)
        self.assertRaises(ValueError, hex2str, INT)
        self.assertRaises(ValueError, hex2str, STR)
        # * -> hexs
        self.assertRaises(ValueError, int2hexs, INT, n_chunks=-1)
        self.assertRaises(ValueError, str2hexs, STR, len_in=-1)
        self.assertRaises(ValueError, bin2hexs, BIN, len_out=-1)

    def test_data_conversion_from_int(self):
        # int -> bin
        self.assertEqual(int2bin(INT), BIN)
        self.assertEqual(int2bin(INT, order="little"), BIN_LE)
        self.assertEqual(int2bin(INT, 8, 5), "10100001011001110100")
        self.assertEqual(int2bin(INT, 8, 2, order="little"), "00110100")
        self.assertRaises(ValueError, int2bin, BIN)
        self.assertRaises(ValueError, int2bin, HEX)
        self.assertRaises(ValueError, int2bin, STR)
        self.assertRaises(ValueError, int2bin, INT, -1)
        self.assertRaises(ValueError, int2bin, INT, 4, -1)
        self.assertRaises(ValueError, int2bin, INT, order="bad_order")
        self.assertEqual(int2bins(INT, n_chunks=2), [BIN[:16], BIN[16:]])
        self.assertEqual(int2bins(INT, len_in=16), [BIN[:16], BIN[16:]])
        self.assertEqual(int2bins(INT, len_out=16), [BIN[:16], BIN[16:]])
        # int -> hex
        self.assertEqual(int2hex(INT), HEX)
        self.assertRaises(ValueError, int2hex, BIN)
        self.assertRaises(ValueError, int2hex, HEX)
        self.assertRaises(ValueError, int2hex, STR)
        self.assertRaises(ValueError, int2hex, INT, 0)
        # int -> str
        self.assertEqual(int2str(INT), STR)
        self.assertEqual(ints2str(29797, 29556), STR)
        self.assertRaises(ValueError, int2hex, BIN)
        self.assertRaises(ValueError, int2hex, HEX)
        self.assertRaises(ValueError, int2hex, STR)
        # int -> uni
        self.assertIsNotNone(ints2uni(1000, 10000, 100000))
        self.assertRaises(UnicodeDecodeError, int2uni, -1)
        self.assertRaises(ValueError, int2uni, BIN)
        self.assertRaises(ValueError, int2uni, HEX)
        self.assertRaises(ValueError, int2uni, STR)
        # * -> ints
        self.assertRaises(ValueError, hex2ints, HEX, n_chunks=-1)
        self.assertRaises(ValueError, str2ints, STR, len_in=-1)
        self.assertRaises(ValueError, bin2ints, BIN, len_out=-1)
        # int -> flags
        self.assertRaises(ValueError, int2flags, HEX)
        self.assertEqual(int2flags(12), [True, True, False, False])
        # flags -> int
        self.assertEqual(flags2int(True, True, False, False), 12)

    def test_data_conversion_from_str(self):
        # str -> bin
        self.assertEqual(str2bin(STR), BIN)
        self.assertRaises(ValueError, str2bin, INT)
        # str -> hex
        self.assertEqual(str2hex(STR), HEX)
        self.assertRaises(ValueError, str2hex, INT)
        # str -> int
        self.assertEqual(str2int(STR), INT)
        self.assertRaises(ValueError, str2int, INT)
        self.assertRaises(ValueError, str2int, STR, -1)
        self.assertEqual(str2ints(STR, n_chunks=2), [29797, 29556])
        # * -> strs
        self.assertRaises(ValueError, hex2strs, HEX, n_chunks=-1)
        self.assertRaises(ValueError, int2strs, INT, len_in=-1)
        self.assertRaises(ValueError, bin2strs, BIN, len_out=-1)
        # str <-> lst
        self.assertEqual(str2lst("abc"), ['a', 'b', 'c'])
        self.assertEqual(str2lst("123"), [1, 2, 3])
        self.assertRaises(ValueError, str2lst, INT)
        self.assertEqual(lst2str(['a', 'b', 'c']), "a,b,c")
        self.assertEqual(lst2str(['a', 'b', 'c'], ""), "abc")
        self.assertEqual(lst2str([1, 2, 3], sep=""), "123")
        self.assertRaises(ValueError, lst2str, INT)
    
    def test_data_conversion_back_and_forth(self):
        for i in range(8, 12):
            self.assertEqual(bin2bin(bin2bin(BIN, nbits_out=i), i), BIN)
            self.assertEqual(hex2bin(bin2hex(BIN, nbits_out=i), i), BIN)
            self.assertEqual(bin2hex(hex2bin(HEX, nbits_out=i), i), HEX)
            self.assertEqual(int2bin(bin2int(BIN, nbits_out=i), i), BIN)
            self.assertEqual(bin2int(int2bin(INT, nbits_out=i), i), INT)
            self.assertEqual(str2bin(bin2str(BIN, nbits_out=i), i), BIN)
            self.assertEqual(bin2str(str2bin(STR, nbits_out=i), i), STR)
        self.assertEqual(hex2str(str2hex(STR)), STR)
        self.assertEqual(str2hex(hex2str(HEX)), HEX)
        self.assertEqual(hex2int(int2hex(INT)), INT)
        self.assertEqual(int2hex(hex2int(HEX)), HEX)
        self.assertEqual(str2int(int2str(INT)), INT)
        self.assertEqual(int2str(str2int(STR)), STR)
    
    def test_other_data_conversions(self):
        DICT = {'test': "Test string", 'data': {'a': 1, 'b': 2}}
        self.assertTrue(json2html(DICT))
        XML = json2xml(DICT)
        self.assertTrue(XML)
        self.assertTrue(xml2json(XML))
        REPORT = """
______________________________________
            A NICE BANNER
______________________________________

[+] URL: http://www.example.com/
[+] Started: Mon Jan 01 12:34:56 3020

Findings:

[+] http://www.example.com/abc
 | Key: Value

[+] http://www.example.com/def
 | Found By: Test
 | List entries:
 |  - /ghi/
 |  - /jkl/
 |
 | Version: 1

[+] Test1
[+] Test1

[i] Other findings:

[+] test
 | Location: http://www.example.com/something
 | Last Updated: 3020-01-01T12:34:57.000Z
 |
 | Found By: Test

[+] Finished: Mon Jan 01 12:34:58 3020
[+] Tests Done: 20

++++++++++++++++++++++++++++
          Footer
++++++++++++++++++++++++++++
        """
        self.assertTrue(report2objects(REPORT, header_sep="_", footer_sep="+"))

