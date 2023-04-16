#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports module assets' tests.

"""
from tinyscript.preimports import *
from tinyscript.preimports import load

from utils import *


class TestPreimports(TestCase):
    def test_preimports(self):
        BAD = "does_not_exist"
        load(BAD, lazy=False)
        self.assertIn(BAD, __imports__['bad'])
        for m in __imports__['standard'] + list(__imports__['enhanced'].keys()):
            self.assertIn(m, globals().keys())
        for m in __imports__['bad']:
            self.assertNotIn(m, globals().keys())

