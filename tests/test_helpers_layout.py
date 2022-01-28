#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""CLI layout objects' tests.

"""
from tinyscript.helpers.layout import *

from utils import TestCase


class TestHelpersLayoutObjects(TestCase):
    def test_borderless_objects(self):
        nd = NameDescription("test", "test argument")
        self.assertNotIn("\n\n", str(nd))
        nd = NameDescription("test", "test argument", "test details")
        self.assertIn("\n\n", str(nd))
        data = [["h1", "h2"], ["v1", "v2"]]
        bt1 = BorderlessTable(data, header=False)
        self.assertIsNotNone(str(bt1))
        self.assertNotIn("-", str(bt1))
        bt2 = BorderlessTable(data)
        self.assertIsNotNone(str(bt2))
        self.assertIn("-", str(bt2))
        self.assertRaises(ValueError, BorderlessTable, "BAD_DATA")
        self.assertRaises(ValueError, BorderlessTable, [])

