#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Compatibility functions' tests.

"""
from tinyscript.helpers.fexec import *

from utils import remove, TestCase


@process
def test1():
    pass


@thread
def test2():
    pass


class TestHelpersFexec(TestCase):
    def test_execution_functions(self):
        self.assertIsNotNone(execute("id"))
        self.assertIsNotNone(test1())
        self.assertIsNotNone(test2())
        self.assertIsNone(processes_clean())
        self.assertIsNone(threads_clean())
        self.assertEqual(apply([lambda x: x+1, lambda x: x+2], (1, )), [2, 3])

