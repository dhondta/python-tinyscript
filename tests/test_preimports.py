#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports module assets' tests.

"""
from tinyscript.preimports import *
from tinyscript.preimports import _load_preimports

from utils import *


class TestPreimports(TestCase):
    def test_preimports(self):
        preimp, fails = _load_preimports("does_not_exist")
        self.assertEqual(PREIMPORTS, preimp)
        self.assertEqual(["does_not_exist"], fails)
        self.assertEqual(PREIMPORTS, _load_preimports()[0])
        for m in PREIMPORTS:
            self.assertIn(m, globals().keys())
        # test the new hashlib function
        touch("test-file.txt")
        self.assertEqual(hashlib.hash_file("test-file.txt"),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        self.assertEqual(hashlib.sha256_file("test-file.txt"),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        with open("test-file.txt", 'w') as f:
            f.write(100 * "A")
        self.assertEqual(hashlib.hash_file("test-file.txt", "md5"),
            "8adc5937e635f6c9af646f0b23560fae")
        self.assertRaises(IOError, hashlib.hash_file, "does_not_exist")
        self.assertRaises(ValueError, hashlib.hash_file,
                          "test-file.txt", "not_existing_hash_algo")
        remove("test-file.txt")
