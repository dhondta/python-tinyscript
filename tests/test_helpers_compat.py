#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Compatibility functions' tests.

"""
from tinyscript.helpers.compat import *

from utils import remove, TestCase


class TestHelpersCompat(TestCase):
    def test_compatibility_functions(self):
        CMD_PY = "print('hello')"
        TEST_PY = "execfile-test.py"
        with open(TEST_PY, 'w') as f:
            f.write(CMD_PY)
        execfile(TEST_PY)
        remove(TEST_PY)
        self.assertEqual(list(iterbytes("test")), [116, 101, 115, 116])
        self.assertRaises(TypeError, ensure_str, [])
        self.assertEqual(ensure_str("test"), "test")
        self.assertRaises(TypeError, ensure_binary, [])
        self.assertEqual(ensure_binary("test"), b("test"))
        self.assertEqual(ensure_binary(b"test"), b("test"))

