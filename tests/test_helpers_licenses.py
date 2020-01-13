#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""License features' tests.

"""
from tinyscript.helpers.licenses import license, LICENSES

from utils import TestCase


class TestHelpersLicenses(TestCase):
    def test_license_getter(self):
        self.assertEqual(license("does_not_exist"), "Invalid license")
        self.assertEqual(license("afl-3.0"), LICENSES['afl-3.0'])
