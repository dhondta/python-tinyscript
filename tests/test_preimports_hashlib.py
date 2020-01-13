#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports hashlib assets' tests.

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
