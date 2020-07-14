#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Template module assets' tests.

"""
from tinyscript.template import new, TARGETS, TEMPLATE

from utils import *


class TestTemplate(TestCase):
    def test_script_generation(self):
        SCR = "test-script"
        new(SCR)
        self.assertTrue(exists(SCR + ".py"))
        with open(SCR + ".py") as f:
            self.assertIn("from tinyscript import *", f.read())
        for t in TARGETS.keys():
            new(SCR, t)
            self.assertTrue(exists(SCR + ".py"))
            with open(SCR + ".py") as f:
                self.assertIn("from {} import {}".format(*t.split(".")), f.read())
        remove(SCR + ".py")

