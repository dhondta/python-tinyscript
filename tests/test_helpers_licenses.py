#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""License features' tests.

"""
from tinyscript.helpers.licenses import *
from tinyscript.helpers.licenses import LICENSES

from utils import TestCase


class TestHelpersLicenses(TestCase):
    def test_license_functions(self):
        self.assertEqual(license("does_not_exist"), "Invalid license")
        self.assertEqual(license("afl-3.0"), LICENSES['afl-3.0'])
        self.assertIsNotNone(list_licenses())
        self.assertIn("test", copyright("test"))
        self.assertIn("2000", copyright("test", 2000))
        self.assertIn("2010", copyright("test", 2000, 2010))

