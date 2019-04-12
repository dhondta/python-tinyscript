#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common help utility help functions' tests.

"""
from unittest import main, TestCase

from tinyscript.helpers.licenses import license, LICENSES


class TestLicenses(TestCase):
    def setUp(self):
        pass
    
    def test_license_getter(self):
        self.assertEqual(license("does_not_exist"), "Invalid license")
        self.assertEqual(license("afl-3.0"), LICENSES['afl-3.0'])


if __name__ == '__main__':
    main()
