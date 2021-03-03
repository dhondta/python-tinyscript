#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Compatibility functions' tests.

"""
import logging
from tinyscript.helpers.fexec import *

from utils import remove, TestCase


logger = logging.getLogger("test-exec-log")


@process
def test1():
    pass


@thread
def test2():
    pass


class TestHelpersFexec(TestCase):
    def test_execution_functions(self):
        self.assertIsNotNone(execute("id"))
        self.assertIsNotNone(execute_and_log("id"))
        self.assertIsNotNone(execute_and_log(["id"], shell=True))
        self.assertIsNotNone(execute_and_log("id 123456789", logger=logging.getLogger("test-exec-log-2")))
        self.assertIsNotNone(filter_bin("cat", "id", "netstat", "whoami"))
        self.assertIsNotNone(test1())
        self.assertIsNotNone(test2())
        self.assertIsNone(processes_clean())
        self.assertIsNone(threads_clean())
        self.assertEqual(apply([lambda x: x+1, lambda x: x+2], (1, )), [2, 3])

