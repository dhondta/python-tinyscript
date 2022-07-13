#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports code inspection assets' tests.

"""
from tinyscript.helpers.data.types import is_module
from tinyscript.preimports import inspect

from utils import *


class TestPreimportsInspect(TestCase):
    def test_get_functions(self):
        m = inspect.getcallermodule()
        self.assertTrue(is_module(m))
        self.assertEqual(m.__name__, "test_preimports_inspect")
        m = inspect.getmainmodule()
        self.assertTrue(is_module(m))
        self.assertIn(m.__name__, ["__main__", "pytest"])
        self.assertIsNotNone(inspect.getmainframe())
        self.assertIn(('__name__', "__main__"), inspect.getmainglobals().items())

