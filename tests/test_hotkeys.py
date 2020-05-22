#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Keystrokes module assets' tests.

"""
from tinyscript.helpers.inputs import _keyboard, hotkeys_enabled
from tinyscript.hotkeys import set_hotkeys

from utils import *


class TestHotkeys(TestCase):
    def test_set_hotkeys(self):
        if hotkeys_enabled:
            temp_stdout(self)
            set_hotkeys({})
            set_hotkeys({'HOTKEYS': "default"})
            _keyboard.press("a")
            _keyboard.press("l")
            set_hotkeys({'HOTKEYS': {'l': "TEST"}})
            _keyboard.press("l")
            set_hotkeys({'HOTKEYS': ("default", {'l': "TEST"})})
            _keyboard.press("l")
            self.assertRaises(ValueError, set_hotkeys, {'HOTKEYS': "BAD"})

