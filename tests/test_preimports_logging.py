#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports logging assets' tests.

"""
from tinyscript.preimports import logging

from utils import *


class TestPreimportsLogging(TestCase):    
    def test_logging_improvements(self):
        l = logging.getLogger("test")
        l.addHandler(logging.StreamHandler())
        logging.setLoggers(globals())
        logging.setLogger(globals(), "test")
