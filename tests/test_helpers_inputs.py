#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Input functions' tests.

"""
from tinyscript.helpers.compat import b
from tinyscript.helpers.inputs import *
from tinyscript.helpers.inputs import _keyboard, hotkeys_enabled
from tinyscript.loglib import logger as ts_logger

from utils import *


class TestHelpersInputs(TestCase):
    def test_input_functions(self):
        clear()
        temp_stdout(self)
        self.assertTrue(b("test"))
        self.assertEqual(b(1), 1)
        temp_stdin(self, "test\n")
        self.assertEqual(std_input(), "test")
        temp_stdin(self, "test\n")
        self.assertEqual(std_input("test", ["red", "green"]), "test")
        temp_stdin(self, "y\n")
        self.assertTrue(confirm())
        temp_stdin(self, "test\n")
        self.assertEqual(user_input(), "test")
        temp_stdin(self, "1\n")
        self.assertTrue(user_input(choices=["1", "2"]))
        temp_stdin(self, "1\n")
        self.assertTrue(user_input(choices=["1", "2"], style="red_on_green"))
        temp_stdin(self, "Yes\n")
        self.assertTrue(user_input(choices=["Yes", "No"]))
        temp_stdin(self, "yes\n")
        self.assertTrue(user_input(choices=["Yes", "No"]))
        temp_stdin(self, "Yes\n")
        self.assertTrue(user_input(choices=["yes", "no"]))
        temp_stdin(self, "y\n")
        self.assertTrue(user_input(choices=["(Y)es", "(N)o"]))
        temp_stdin(self, "\n")
        self.assertEqual(user_input(default="test"), "test")
        temp_stdin(self, "test\n")
        self.assertEqual(user_input(choices=lambda v: v in ["test"]), "test")
        temp_stdin(self, "bad\n")
        self.assertIs(user_input(choices=["1", "2"]), None)
    
    def test_capture_functions(self):
        with Capture() as (out, err):
            print("987654321")
            ts_logger.info("123456789")
        self.assertEqual("987654321", out.text)
        self.assertIn("123456789", err.text)
        def dummy(): print("TEST")
        silent_dummy = silent(dummy)
        with Capture() as (out, err):
            silent_dummy()
        self.assertEqual(str(repr(out)), "")
        captured_dummy = capture(dummy)
        r, out, err = captured_dummy()
        self.assertEqual(out, "TEST")
    
    def test_keystrokes_function(self):
        if hotkeys_enabled:
            temp_stdout(self)
            hotkeys({'t': "TEST"})
            _keyboard.type("t")
            hotkeys({'t': ("TEST", sys.stdout)})
            _keyboard.type("t")
            hotkeys({'t': ("TEST", ts_logger.info)})
            _keyboard.type("t")
            hotkeys({'t': ("TEST", "BAD_OUTPUT_HANDLER")}, False)
            with self.assertRaises(ValueError):
                _keyboard.press("a")
            with self.assertRaises(TypeError):
                _keyboard.press("t")
            hotkeys({'ctrl': ("CTRL", ts_logger.info)})
            from tinyscript.helpers.inputs import Key
            _keyboard.press(Key.ctrl)

