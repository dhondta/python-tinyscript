# -*- coding: UTF-8 -*-
"""Root module's __conf__.py tests.

"""
from tinyscript import *

from utils import *


class TestConf(TestCase):
    def test_deprecation(self):
        self.assertWarns(DeprecationWarning, deprecate, "test", "test2")
        f = lambda x: x
        f.__name__ = "test"
        deprecate(f, "test2")
        self.assertWarns(DeprecationWarning, test, "ok")

    def test_lazy_loading(self):
        lazy_load_module("gc", preload=lambda: True, postload=lambda m: True)
        self.assertIsNotNone(gc.DEBUG_LEAK)
        lazy_load_object("test", lambda: "ok", preload=lambda: True, postload=lambda m: True)
        self.assertIsNotNone(test.center(20))

