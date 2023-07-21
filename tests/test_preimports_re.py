#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports regular expression assets' tests.

"""
from tinyscript.preimports import re

from utils import *


class TestPreimportsRe(TestCase):
    def test_re_strings_generation(self):
        len = lambda g: sum(1 for _ in g)
        self.assertEqual(list(re.strings(None)), [])
        self.assertTrue(re.randstr(r"abc").startswith("abc"))
        word = re.randstr(r"abc(def|ghi|jkl)")
        self.assertTrue(any(s in word for s in ["def", "ghi", "jkl"]))
        for i in range(20):
            self.assertEqual(re.randstr(r"[a]"), "a")
            self.assertTrue("a" not in re.randstr(r"[^a]"))
        self.assertEqual(len(re.randstrs(r"\D", 10)), 10)
        self.assertEqual(len(re.strings(r"[a]")), 1)
        self.assertEqual(len(re.randstrs(r"[a]", 10)), 10)
        self.assertEqual(len(re.strings(r"[ab]")), 2)
        self.assertEqual(len(re.strings(r"^[a]?$")), 2)
        self.assertEqual(len(re.randstrs(r"[ab]", 10)), 10)
        self.assertEqual(len(re.strings(r"[ab]{2}")), 4)
        self.assertEqual(len(re.strings(r"[ab]{1,2}")), 6)
        self.assertEqual(len(re.strings(r"[ab]{1,2}[0-3]{3}")), 384)
        self.assertTrue(all(s.startswith("a") and any(s.endswith(c) for c in "bcd") for s in re.strings(r"a(b|c|d)")))
        self.assertEqual(re.size(None), 0)
        self.assertEqual(re.size(r".*", "inf"), float("inf"))
        self.assertEqual(re.size(r"(test)*\1", "inf"), float("inf"))
        self.assertEqual(re.size(r"(?:a|b)+", "inf"), float("inf"))
        self.assertEqual(re.size(r"[a-z]*", "inf"), float("inf"))
        for regex in [r"[ab]{1,3}.", r"(?<=ab)cd", r"(?<=-)\w+", r"([^\s])\1", r"[^\\]", r"(|[0-5])?"]:
            g = re.strings(regex)
            for i in range(min(50, re.size(regex))):
                self.assertIsNotNone(next(g))
#                self.assertEqual(len(re.strings(regex, 1)), re.size(regex, 1))
        for regex in [r"abc(1|2|3){1,3}", r"[ab]{1,2}c[d-eD0-3]"]:
            self.assertEqual(len(re.strings(regex)), re.size(regex))

