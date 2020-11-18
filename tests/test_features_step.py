#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Stepping module assets' tests.

"""
from tinyscript.features.step import set_step_items

from utils import *


args.step = True
set_step_items(globals())


class TestStepping(TestCase):
    def test_step_setup(self):
        g = globals().keys()
        self.assertTrue(args.step)
        self.assertIn("step", g)
        self.assertIn("Step", g)

    def test_step_object(self):
        temp_stdout(self)
        temp_stdin(self, "\n")
        with Step("test"):
            pass
        temp_stdin(self, "\n")
        with Step():
            pass
        temp_stdin(self, "\n")
        with Step(at_end=True):
            pass
    
    def test_step_function(self):
        temp_stdout(self)
        temp_stdin(self, "\n")
        self.assertIs(step(), None)
        temp_stdin(self, "\n")
        self.assertIs(step("test"), None)

