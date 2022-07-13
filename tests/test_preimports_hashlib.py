#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports hashing assets' tests.

"""
from tinyscript.preimports import hashlib

from utils import *


FILE = "test-file.txt"


class TestPreimportsHashlib(TestCase):
    def test_hashlib_improvements(self):
        touch(FILE)
        self.assertEqual(hashlib.hash_file(FILE),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        self.assertEqual(hashlib.sha256_file(FILE),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        with open(FILE, 'w') as f:
            f.write(100 * "A")
        self.assertEqual(hashlib.hash_file(FILE, "md5"),
                         "8adc5937e635f6c9af646f0b23560fae")
        self.assertRaises(IOError, hashlib.hash_file, "does_not_exist")
        self.assertRaises(ValueError, hashlib.hash_file, FILE,
                          "not_existing_hash_algo")
        remove(FILE)
    
    def test_hashlib_lookup_table(self):
        touch(FILE)
        with open(FILE, 'w') as f:
            f.write("12345678\nabcdefghi")
        self.assertEqual(hashlib.LookupTable(FILE), {'25d55ad283aa400af464c76d713c07ad': "12345678",
                                                     '8aa99b1f439ff71293e95357bac6fd94': "abcdefghi"})
        self.assertEqual(hashlib.LookupTable(FILE, prefix="test:"), {'c6b921e20761fcd95c9cc141389b10db': "12345678",
                                                                     'ecfb190ec68ec6ada41cf487f5d076ce': "abcdefghi"})
        self.assertEqual(hashlib.LookupTable(FILE, dict_filter=lambda x: x.isdigit()),
                         {'25d55ad283aa400af464c76d713c07ad': "12345678"})
        self.assertRaises(ValueError, hashlib.LookupTable, "does_not_exist")
        self.assertRaises(ValueError, hashlib.LookupTable, FILE, "bad_hash_algorithm")
        self.assertRaises(ValueError, hashlib.LookupTable, FILE, "md5", "bad_ratio")
        remove(FILE)

