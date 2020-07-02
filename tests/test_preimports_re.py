#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports re assets' tests.

"""
from tinyscript.preimports import re

from utils import *


class TestPreimportsRe(TestCase):
    def test_re_strings_generation(self):
        self.assertEqual(list(re.randstrs(None)), [])
        self.assertTrue(re.randstr(r"abc").startswith("abc"))
        word = re.randstr(r"abc(def|ghi|jkl)")
        self.assertTrue(any(s in word for s in ["def", "ghi", "jkl"]))
        for i in range(20):
            self.assertEqual(re.randstr(r"[a]"), "a")
            self.assertTrue("a" not in re.randstr(r"[^a]"))
        self.assertEqual(len(list(re.randstrs(r"\D", 10))), 10)
        self.assertEqual(len(list(re.randstrs(r"[a]", 10))), 1)
        self.assertEqual(len(list(re.randstrs(r"[ab]", 10))), 2)
        self.assertEqual(len(list(re.strings(r"[ab]{2}"))), 4)
        self.assertEqual(len(list(re.strings(r"[ab]{1,2}"))), 6)
        self.assertTrue(all(s.startswith("a") and any(s.endswith(c) for c in "bcd") for s in re.randstrs(r"a(b|c|d)")))
        self.assertIsNotNone(list(re.randstrs(r"[ab]{1,3}")))
        self.assertIsNotNone(list(re.randstrs(r"(?<=ab)cd")))
        self.assertIsNotNone(list(re.randstrs(r"(?<=-)\w+")))
        self.assertIsNotNone(list(re.randstrs(r"([^\s])\1")))
        self.assertIsNotNone(list(re.randstrs(r"[^\\]")))
        self.assertIsNotNone(list(re.randstrs(r"(|[0-5])?")))
        self.assertIsNotNone(list(re.randstrs(r"^\S{10,30}")))
        self.assertIsNotNone(list(re.randstrs(r"[^a].[a]*", 10)))

