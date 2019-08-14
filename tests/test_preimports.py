#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports module assets' tests.

"""
from tinyscript.preimports import *
from tinyscript.preimports import _load_preimports

from utils import *


class TestPreimports(TestCase):
    def test_preimports(self):
        BAD = "does_not_exist"
        _load_preimports(BAD)
        self.assertIn(BAD, __badimports__)
        for m in __optimports__ + __preimports__:
            self.assertIn(m, globals().keys())
        for m in __badimports__:
            self.assertNotIn(m, globals().keys())

    def test_hashlib_improvements(self):
        FILE = "test-file.txt"
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
