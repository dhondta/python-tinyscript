#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Interaction module assets' tests.

"""
from tinyscript.interact import set_interact_items

from utils import *


args.interact = True
set_interact_items(globals())


class TestInteraction(TestCase):    
    def test_interact_setup(self):
        self.assertTrue(args.interact)
        self.assertIn("interact", globals().keys())
        self.assertIn("compile_command", globals().keys())
        self.assertIn("InteractiveConsole", globals().keys())
        self.assertIn("RemoteInteractiveConsole", globals().keys())

    def test_local_interaction(self):
        temp_stdout(self)
        temp_stdin(self, "\n")
        self.assertIs(interact(), None)
    
    def test_local_interactive_console(self):
        temp_stdout(self)
        temp_stdin(self, "\n")
        with InteractiveConsole() as console:
            self.assertIs(console.interact(), None)
