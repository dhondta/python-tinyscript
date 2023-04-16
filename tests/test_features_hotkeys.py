#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Keystrokes module assets' tests.

"""
from time import sleep
from tinyscript.features.hotkeys import set_hotkeys
from tinyscript.helpers.inputs import _keyboard

from utils import *


class TestHotkeys(TestCase):
    def test_set_hotkeys(self):
        try:  # do not check with 'if _keyboard is None:' ; _keyboard's type will be lazy_proxy_object.Proxy
            _keyboard.press
        except AttributeError:  # 'NoneType' object has no attribute 'press'
            return
        temp_stdout(self)
        set_hotkeys({})
        set_hotkeys({'HOTKEYS': "default"})
        sleep(.1)
        _keyboard.press("a")
        sleep(.1)
        _keyboard.press("l")
        sleep(.1)
        set_hotkeys({'HOTKEYS': {'l': "TEST"}})
        sleep(.1)
        _keyboard.press("l")
        sleep(.1)
        set_hotkeys({'HOTKEYS': ("default", {'l': "TEST"})})
        sleep(.1)
        _keyboard.press("l")
        sleep(.1)
        self.assertRaises(ValueError, set_hotkeys, {'HOTKEYS': "BAD"})

