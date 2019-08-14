#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Code patching functions' tests.

"""
from unittest import TestCase

from tinyscript.helpers.patch import *
from tinyscript.helpers.patch import PatchError

from utils import *


def dummy1(): return 1


def dummy2():
    # useless comment
    return 1


def dummy3():
    # version: 1
    return 1


class TestHelpersCode(TestCase):
    def test_function_replacement(self):
        # this will use patchy.replace
        code_replace(dummy1, "def dummy1(): return 1", "def dummy1(): return 42")
        self.assertEqual(dummy1(), 42)
        # this will trigger string replacements before using patchy.replace
        code_replace(dummy1, "return 42", "return 2*42")
        self.assertEqual(dummy1(), 84)
        code_replace(dummy1, "return 2*42", "return 3*42")
        self.assertEqual(dummy1(), 126)
        # this will trigger an error as the replacement has a bad format
        self.assertRaises(PatchError, code_replace, dummy1, "bad")    

    def test_function_line_operations(self):
        # this will modify lines by index
        code_replace_line(dummy2, 1, "# useless modified comment")
        self.assertIn("useless modified comment", code_source(dummy2))
        code_add_line(dummy2, 1, "# another useless comment before first")
        code_add_line(dummy2, 2, "pass", after=True)
        self.assertEqual(len(code_source(dummy2).split("\n")), 5)
        code_remove_line(dummy2, -1)
        self.assertIsNone(dummy2())
        code_replace_lines(dummy2, 1, None, -1, "return 42")
        self.assertEqual(len(code_source(dummy2).split("\n")), 3)
        self.assertEqual(dummy2(), 42)
        # this will trigger an error as the replacement has a bad format
        self.assertRaises(PatchError, code_add_lines, dummy2, "test", "test")
        self.assertRaises(PatchError, code_add_lines, dummy2, 0, 0)
        self.assertRaises(PatchError, code_add_lines, dummy2, 15, "test")
        self.assertRaises(PatchError, code_add_lines, dummy2, -12, "test")
        self.assertRaises(PatchError, code_add_lines, dummy2, 0, "test", 0, "")
        self.assertRaises(PatchError, code_replace_lines, dummy2, 0)
        self.assertRaises(PatchError, code_replace_lines, dummy2, 0, "t", 0, "")
        self.assertRaises(PatchError, code_delete_lines, dummy2, 0, 0)
        # this will add some non-indented lines and check the new function
        code_add_line(dummy2, -1, "return 2*42")
        code_add_lines(dummy2, -1, "return 12345",
                               -2, "# this return will not execute")
        self.assertEqual(len(code_source(dummy2).split("\n")), 6)
        self.assertEqual(dummy2(), 84)
        code_add_line(dummy2, 1, "return 3*42")
        self.assertEqual(dummy2(), 126)
        code_add_line(dummy2, 1, "return 4*42", after=True)
        self.assertEqual(dummy2(), 126)
        code_add_line(dummy2, 0, "# dummy function")
        self.assertEqual(len(code_source(dummy2).split("\n")), 9)
        code_delete_lines(dummy2, -1, -2, -3, -4)
        self.assertEqual(len(code_source(dummy2).split("\n")), 5)
        code_add_block(dummy2, 1, code_source(dummy3), after=True)
        self.assertIn("# version: 1", code_source(dummy2))
    
    def test_function_code_restore(self):
        # no modification yet ; code_restore should return False
        self.assertFalse(code_restore(dummy3))
        # now apply some modifications
        self.assertIn("version: 1", code_source(dummy3))
        code_replace_lines(dummy3, 1, "# version: 2")
        self.assertIn("version: 2", code_source(dummy3))
        code_replace_lines(dummy3, 1, "# version: 3")
        self.assertIn("version: 3", code_source(dummy3))
        code_replace_lines(dummy3, 1, "# version: 4")
        self.assertIn("version: 4", code_source(dummy3))
        code_replace_lines(dummy3, 1, "# version: 5")
        self.assertIn("version: 5", code_source(dummy3))
        # test maximum 3 reverts
        self.assertTrue(code_revert(dummy3))
        self.assertTrue(code_revert(dummy3))
        self.assertTrue(code_revert(dummy3))
        self.assertFalse(code_revert(dummy3))
        # now replace once again and try to restore
        code_replace_lines(dummy3, 1, "# version: 7")
        self.assertIn("version: 7", code_source(dummy3))
        code_restore(dummy3)
        self.assertIn("version: 1", code_source(dummy3))
        self.assertEqual(dummy3(), 1)
