#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Interaction module assets' tests.

"""
from tinyscript.interact import set_interact_items

from utils import *


args.interact = True
set_interact_items(globals())


class TestInteraction(TestCase):    
    def test_local_interaction(self):
        temp_stdin(self, "\n")
        temp_stdout(self)
        self.assertIs(interact(), None)
    
    def test_local_interactive_console(self):
        temp_stdin(self, "\n")
        temp_stdout(self)
        with InteractiveConsole() as console:
            self.assertIs(console.interact(), None)
