#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports code manipulation assets' tests.

"""
from tinyscript.preimports import code

from utils import *


def dummy1():
    return 1


def dummy2():
    # useless comment
    return 1


def dummy3():
    # version: 1
    return 1


class TestPreimportsCode(TestCase):
    def test_function_replacement(self):
        self.assertRaises(ValueError, code.replace, code, "", "")
        # this will use patchy.replace
        code.replace(dummy1, "def dummy1(): return 1", "def dummy1(): return 42")
        self.assertEqual(dummy1(), 42)
        # this will trigger string replacements before using patchy.replace
        code.replace(dummy1, "return 42", "return 2*42")
        self.assertEqual(dummy1(), 84)
        code.replace(dummy1, "return 2*42", "return 3*42")
        self.assertEqual(dummy1(), 126)
        # this will trigger an error as the replacement has a bad format
        self.assertRaises(code.PatchError, code.replace, dummy1, "bad")    

    def test_function_line_operations(self):
        # this will modify lines by index
        code.replace_line(dummy2, 1, "# useless modified comment")
        self.assertIn("useless modified comment", code.source(dummy2))
        code.add_line(dummy2, 1, "# another useless comment before first")
        code.add_line(dummy2, 2, "pass", after=True)
        self.assertEqual(len(code.source(dummy2).split("\n")), 5)
        code.remove_line(dummy2, -1)
        self.assertIsNone(dummy2())
        code.replace_lines(dummy2, 1, None, -1, "return 42")
        self.assertEqual(len(code.source(dummy2).split("\n")), 3)
        self.assertEqual(dummy2(), 42)
        # this will trigger an error as the replacement has a bad format
        self.assertRaises(code.PatchError, code.add_lines, dummy2, "test", "test")
        self.assertRaises(code.PatchError, code.add_lines, dummy2, 0, 0)
        self.assertRaises(code.PatchError, code.add_lines, dummy2, 15, "test")
        self.assertRaises(code.PatchError, code.add_lines, dummy2, -12, "test")
        self.assertRaises(code.PatchError, code.add_lines, dummy2, 0, "test", 0, "")
        self.assertRaises(code.PatchError, code.replace_lines, dummy2, 0)
        self.assertRaises(code.PatchError, code.replace_lines, dummy2, 0, "t", 0, "")
        self.assertRaises(code.PatchError, code.delete_lines, dummy2, 0, 0)
        # this will add some non-indented lines and check the new function
        code.add_line(dummy2, -1, "return 2*42")
        code.add_lines(dummy2, -1, "return 12345", -2, "# this return will not execute")
        self.assertEqual(len(code.source(dummy2).split("\n")), 6)
        self.assertEqual(dummy2(), 84)
        code.add_line(dummy2, 1, "return 3*42")
        self.assertEqual(dummy2(), 126)
        code.add_line(dummy2, 1, "return 4*42", after=True)
        self.assertEqual(dummy2(), 126)
        code.add_line(dummy2, 0, "# dummy function")
        self.assertEqual(len(code.source(dummy2).split("\n")), 9)
        code.delete_lines(dummy2, -1, -2, -3, -4)
        self.assertEqual(len(code.source(dummy2).split("\n")), 5)
        code.add_block(dummy2, 1, code.source(dummy3), after=True)
        self.assertIn("# version: 1", code.source(dummy2))
    
    def test_function_code_restore(self):
        # no modification yet ; code.restore should return False
        self.assertFalse(code.restore(dummy3))
        # now apply some modifications
        self.assertIn("version: 1", code.source(dummy3))
        code.replace_lines(dummy3, 1, "# version: 2")
        self.assertIn("version: 2", code.source(dummy3))
        code.replace_lines(dummy3, 1, "# version: 3")
        self.assertIn("version: 3", code.source(dummy3))
        code.replace_lines(dummy3, 1, "# version: 4")
        self.assertIn("version: 4", code.source(dummy3))
        code.replace_lines(dummy3, 1, "# version: 5")
        self.assertIn("version: 5", code.source(dummy3))
        # test maximum 3 reverts
        self.assertTrue(code.revert(dummy3))
        self.assertTrue(code.revert(dummy3))
        self.assertTrue(code.revert(dummy3))
        self.assertFalse(code.revert(dummy3))
        # now replace once again and try to restore
        code.replace_lines(dummy3, 1, "# version: 7")
        self.assertIn("version: 7", code.source(dummy3))
        code.restore(dummy3)
        self.assertIn("version: 1", code.source(dummy3))
        self.assertEqual(dummy3(), 1)

