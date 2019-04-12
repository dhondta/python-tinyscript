#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports module assets' tests.

"""
from tinyscript.preimports import *
from tinyscript.preimports import __features__, PREIMPORTS

from utils import *


class TestPreimports(TestCase):
    def test_preimports(self):
        for f in __features__:
            self.assertIn(f, globals().keys())
        for m in PREIMPORTS:
            self.assertIn(m, globals().keys())
