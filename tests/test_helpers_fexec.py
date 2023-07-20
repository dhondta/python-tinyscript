#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Execution functions' tests.

"""
from tinyscript import logging, shutil
from tinyscript.helpers.constants import LINUX
from tinyscript.helpers.fexec import *
from tinyscript.helpers.path import Path, TempPath

from utils import remove, TestCase


logger = logging.getLogger("test-exec-log")


TEST_SH = """#!/bin/bash
while true; do sleep .1; echo "."; >&2 echo "PATTERN$(echo $((1 + $RANDOM % 3)))"; done"""


@process
def test1():
    pass


@thread
def test2():
    pass


class TestHelpersFexec(TestCase):
    @classmethod
    def setUpClass(cls):
        global SH, TPATH
        TPATH = TempPath(prefix="tinyscript-test_", length=8)
        if LINUX:
            SH = TPATH.joinpath("test.sh")
            SH.write_text(TEST_SH)
    
    @classmethod
    def tearDownClass(cls):
        TPATH.remove()
    
    def test_execution_functions(self):
        if LINUX:
            self.assertIsNotNone(execute("id"))
            self.assertIsNotNone(execute("sleep 10", timeout=1))
            self.assertIsNotNone(execute("sleep 10", shell=True, timeout=1))
            self.assertRaises(Exception, execute, "sleep 10", timeout=1, reraise=True)
            self.assertIsNotNone(execute(Path(shutil.which("id"))))
            self.assertIsNotNone(execute_and_log("id"))
            self.assertIsNotNone(execute_and_log(["id"], shell=True))
            self.assertIsNotNone(execute_and_log("id 123456789", logger=logging.getLogger("test-exec-log-2")))
            out, err, retc = execute_and_kill("id", patterns=["TEST"])
            self.assertIsNotNone(out)
            self.assertEqual(retc, 0)
            out, err, retc = execute_and_kill(["/bin/bash", str(SH)], patterns=["PATTERN1"])
            self.assertIn(b"PATTERN1", err)
            self.assertNotEqual(retc, 0)
            self.assertIsNotNone(filter_bin("cat", "id", "netstat", "whoami"))
        self.assertIsNotNone(test1())
        self.assertIsNotNone(test2())
        self.assertIsNone(processes_clean())
        self.assertIsNone(threads_clean())
        self.assertEqual(apply([lambda x: x+1, lambda x: x+2], (1, )), [2, 3])

