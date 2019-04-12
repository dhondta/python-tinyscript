#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Stepping module assets' tests.

"""
from tinyscript.step import set_step_items

from utils import *


args.step = True
set_step_items(globals())


class TestStepping(TestCase):
    def test_step_object(self):
        temp_stdin(self, "\n")
        temp_stdout(self)
        with Step():
            self.assertTrue(Step())
    
    def test_step_function(self):
        temp_stdin(self, "\n")
        temp_stdout(self)
        self.assertIs(step(), None)
