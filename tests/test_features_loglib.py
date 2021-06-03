#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Logging module assets' tests.

"""
from tinyscript.features.loglib import *

from utils import *


class TestLogging(TestCase):
    def setUp(self):
        args.verbose = True
        configure_logger(globals(), False)
    
    def tearDown(self):
        args.verbose = False
        configure_logger(globals(), False)

    def test_base_logger(self):
        temp_stdout(self)
        self.assertIsNot(logger, None)
        self.assertIs(logger.info("test"), None)
        self.assertIs(logger.warning("test"), None)
        self.assertIs(logger.error("test"), None)
        self.assertIs(logger.critical("test"), None)
        self.assertIs(logger.debug("test"), None)
    
    def test_enhanced_logger(self):
        temp_stdout(self)
        configure_logger(globals(), False, True)
        self.assertIs(logger.success("test"), None)
        self.assertIs(logger.failure("test"), None)
        self.assertIs(logger.time("test"), None)
        self.assertIs(logger.step("test"), None)
        self.assertIs(logger.interact("test"), None)
        self.assertIsNot(logging.RelativeTimeColoredFormatter().format(FakeLogRecord()), None)
    
    def test_multi_level_debug(self):
        temp_stdout(self)
        args.verbose = 3
        configure_logger(globals(), True)
        self.assertIs(logger.debug("test"), None)
        delattr(args, "verbose")
        configure_logger(globals(), True)
        self.assertIs(logger.critical("test"), None)

