#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports shutil assets' tests.

"""
from tinyscript.preimports import shutil

from utils import *


class TestPreimportsShutil(TestCase):
    def test_shutil_improvements(self):
        shutil.which("ls")
        self.assertIsNone(shutil.which("this_program_does_not_exist"))

