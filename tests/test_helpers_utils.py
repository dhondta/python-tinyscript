#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common utility help functions' tests.

"""
from unittest import TestCase

from tinyscript.helpers.utils import *

from utils import *


class TestHelpersUtils(TestCase):
    def test_utility_functions(self):
        temp_stdout(self)
        self.assertTrue(b("test"))
        self.assertEqual(b(1), 1)
        temp_stdin(self, "test\n")
        self.assertEqual(std_input(), "test")
        temp_stdin(self, "test\n")
        self.assertEqual(std_input("test", {}), "test")
        temp_stdin(self, "test\n")
        self.assertEqual(user_input(), "test")
        temp_stdin(self, "1\n")
        self.assertTrue(user_input(choices=["1", "2"]))
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
