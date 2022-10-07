#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common utility functions' tests.

"""
from tinyscript.helpers.common import *

from utils import remove, TestCase


class TestHelpersCommon(TestCase):
    def test_common_utility_functions(self):
        self.assertRaises(TypeError, range2, ())
        self.assertRaises(TypeError, range2, 1, 2, 3, 4)
        self.assertEqual(list(range2(2)), [0.0, 1.0])
        self.assertEqual(list(range2(0, .5)), [0.0])
        self.assertEqual(len(range2(0, .5)), 1)
        r = range2(0, .5, .1)
        self.assertEqual(list(r), [0.0, 0.1, 0.2, 0.3, 0.4])
        self.assertEqual(r.count(.5), 0)
        self.assertEqual(r.index(.2), 2)
        self.assertEqual(human_readable_size(123456), "121KB")
        self.assertRaises(ValueError, human_readable_size, "BAD")
        self.assertRaises(ValueError, human_readable_size, -1)
        self.assertIsNotNone(is_admin())
        self.assertEqual(xor("this is a test", " "), "THIS\x00IS\x00A\x00TEST")
        self.assertEqual(list(strings("this is a \x00 test")), ["this is a ", " test"])
        FILE, CONTENT = ".test_strings", b"this is a \x00 test"
        with open(FILE, 'wb') as f:
            f.write(CONTENT)
        self.assertIsNone(xor_file(FILE, " "))
        self.assertIsNone(xor_file(FILE, " "))
        with open(FILE, 'rb') as f:
            self.assertEqual(f.read(), CONTENT)
        self.assertEqual(list(strings_from_file(FILE)), ["this is a ", " test"])
        remove(FILE)

