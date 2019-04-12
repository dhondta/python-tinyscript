#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports module assets' tests.

"""
from tinyscript.preimports import *
from tinyscript.preimports import __features__

from utils import *


class TestPreimports(TestCase):
    def test_preimports(self):
        g = globals().keys()
        for f in __features__:
            self.assertIn(f, g)
