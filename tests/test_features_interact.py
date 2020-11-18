#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Interaction module assets' tests.

"""
from tinyscript.features.interact import set_interact_items

from utils import *


args.interact = True
set_interact_items(globals())


class TestInteraction(TestCase):    
    def test_interact_setup(self):
        g = globals().keys()
        self.assertTrue(args.interact)
        self.assertIn("interact", g)
        self.assertIn("compile_command", g)
        self.assertIn("InteractiveConsole", g)
        self.assertIn("RemoteInteractiveConsole", g)

    def test_local_interaction(self):
        temp_stdout(self)
        temp_stdin(self, "\n")
        self.assertIs(interact(), None)
        temp_stdin(self, "\n")
        self.assertIs(interact("test"), None)
        temp_stdin(self, "\n")
        self.assertIs(interact(exitmsg="test"), None)
    
    def test_local_interactive_console(self):
        temp_stdout(self)
        temp_stdin(self, "\n")
        with InteractiveConsole("test") as console:
            pass
        temp_stdin(self, "\n")
        with InteractiveConsole(exitmsg="test") as console:
            pass
        temp_stdin(self, "\n")
        with InteractiveConsole() as console:
            console.interact()

