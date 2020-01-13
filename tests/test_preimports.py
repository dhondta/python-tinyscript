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
        self.assertIn(BAD, __imports__['bad'])
        for m in __imports__['standard'] + __imports__['enhanced']:
            self.assertIn(m, globals().keys())
        for m in __imports__['bad']:
            self.assertNotIn(m, globals().keys())
