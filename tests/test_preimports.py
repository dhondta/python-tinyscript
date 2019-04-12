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
