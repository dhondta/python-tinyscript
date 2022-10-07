#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Keystrokes module assets' tests.

"""
from time import sleep
from tinyscript.features.hotkeys import set_hotkeys
from tinyscript.helpers.inputs import _keyboard, hotkeys_enabled

from utils import *


def _press(*keys):
    for i in range([5, 1][PYTHON3]):
        for key in keys:
            _keyboard.press(key)
            if not PYTHON3:
                sleep(.1)


class TestHotkeys(TestCase):
    def test_set_hotkeys(self):
        if hotkeys_enabled:
            temp_stdout(self)
            set_hotkeys({})
            set_hotkeys({'HOTKEYS': "default"})
            _press("a", "l")
            set_hotkeys({'HOTKEYS': {'l': "TEST"}})
            _press("l")
            set_hotkeys({'HOTKEYS': ("default", {'l': "TEST"})})
            _press("l")
            self.assertRaises(ValueError, set_hotkeys, {'HOTKEYS': "BAD"})

