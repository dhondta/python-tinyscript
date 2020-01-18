#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Compatibility functions' tests.

"""
from tinyscript.helpers.common import *

from utils import TestCase


class TestHelpersCommon(TestCase):
    def test_common_utility_functions(self):
        self.assertEqual(list(bruteforce(2, "ab")),
                         ["a", "b", "aa", "ab", "ba", "bb"])
        self.assertIsNotNone(execute("id"))
