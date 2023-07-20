#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Input functions' tests.

"""
from tinyscript.features.loglib import logger as ts_logger
from tinyscript.helpers.compat import b
from tinyscript.helpers.constants import TTY
from tinyscript.helpers.inputs import *
from tinyscript.helpers.inputs import _keyboard

from utils import *


class TestHelpersInputs(TestCase):
    def test_input_functions(self):
        clear()
        temp_stdout(self)
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
        temp_stdin(self, "\n")
        self.assertIs(user_input(), None)
        temp_stdin(self, "bad\n1\n")
        self.assertIsNotNone(user_input(choices=["1", "2"], required=True))
    
    def test_capture_functions(self):
        with Capture() as (out, err):
            print("987654321")
            ts_logger.info("123456789")
        self.assertEqual("987654321", out.text)
        self.assertIn("123456789", err.text)
        def dummy(): print("TEST")
        silent_dummy = silent(dummy)
        with Capture(err=False) as out:
            silent_dummy()
        self.assertEqual(str(repr(out)), "")
        captured_dummy = capture(dummy)
        r, out, err = captured_dummy()
        self.assertEqual(out, "TEST")
    
    def test_keystrokes_function(self):
        try:  # do not check with 'if _keyboard is None:' ; _keyboard's type will be lazy_proxy_object.Proxy
            _keyboard.press
        except AttributeError:  # 'NoneType' object has no attribute 'press'
            return
        temp_stdout(self)
        hotkeys({'t': "TEST"})
        _keyboard.type("t")
        hotkeys({'t': ("TEST", sys.stdout)})
        _keyboard.type("t")
        hotkeys({'t': ("TEST", ts_logger.info)})
        _keyboard.type("t")
        hotkeys({'t': ("TEST", "BAD_OUTPUT_HANDLER")}, False)
        if not WINDOWS:
            with self.assertRaises(ValueError):
                _keyboard.press("a")
        with self.assertRaises(TypeError):
            _keyboard.press("t")
        hotkeys({'ctrl': ("CTRL", ts_logger.info)})
        _keyboard.press(Key.ctrl)
    
    def test_styling_functions(self):
        STR = "test string"
        self.assertIsNotNone(colored(STR, "green"))
        self.assertRaises(ValueError, colored, STR, "BAD_COLOR")
        self.assertRaises(ValueError, colored, STR, "bold")
        self.assertIsNotNone(colored(STR, "black", "green"))
        self.assertRaises(ValueError, colored, STR, "black", "BAD_COLOR")
        self.assertRaises(ValueError, colored, STR, "black", "bold")
        self.assertIsNotNone(colored(STR, "black", "green", "bold"))
        self.assertRaises(ValueError, colored, STR, "black", "green", "BAD_MODIFIER")
        self.assertRaises(ValueError, colored, STR, "black", "green", "red")
        self.assertRaises(ValueError, colored, STR, "black", "green", ["bold", "BAD_MODIFIER"])
        self.assertIsNotNone(colored(STR, style="bold_on_green"))
        self.assertIsNotNone(colored(STR, style=["bold", "underlined", "green"]))
        self.assertIsNotNone(colored(STR, palette="solarized"))
        # style argument has precedence on color, on_color and attrs
        a = getattr(self, "assert%sEqual" % ["", "Not"][TTY])
        a(colored(STR, "black", "green", "bold"), colored(STR, "black", "green", "bold", "bold_yellow_on_red"))
        self.assertIsNotNone(colored(STR, "bold", style="bold_yellow_on_red"))
        if TTY:
            self.assertRaises(AttributeError, colored, STR, style="BAD_STYLE")

