#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports logging assets' tests.

"""
from tinyscript.preimports import logging, os, sys

from utils import *


@logging.bindLogger
def f_with_logging(testcase, **kwargs):
    logger.info("OK")
    testcase.assertEqual(logger.name, "other")


class LoggingInFunc(object):
    def f1(self, testcase):
        testcase.assertRaises(AttributeError, getattr, self, "logger")
    
    @logging.bindLogger
    def f2(self, testcase, **kwargs):
        logger.info("OK")
        testcase.assertEqual(self.logger.name, "other")


class TestPreimportsLogging(TestCase):
    def test_log_levels(self):
        self.assertRaises(ValueError, logging.addLogLevel, "info", "yellow", 10)
        levelname = "test"
        self.assertIsNone(logging.addLogLevel(levelname, "cyan", 1))
        self.assertTrue(hasattr(logging, levelname.upper()))
        l = logging.getLogger("test_logger")
        self.assertTrue(hasattr(l, levelname))
        self.assertIsNone(logging.delLogLevel(levelname))
        self.assertRaises(ValueError, logging.delLogLevel, "does_not_exist")
        self.assertFalse(hasattr(logging, levelname.upper()))
        l = logging.getLogger("test_logger")
        self.assertFalse(hasattr(l, levelname))
        self.assertIsNone(logging.addLevelName(100, levelname))
        self.assertIsNone(logging.delLevelName(100))
        self.assertIsNone(logging.addLevelName(100, levelname))
        self.assertIsNone(logging.delLevelName(levelname))
        self.assertIsNone(logging.setLoggingLevel("WARNING", r"test_"))
        self.assertEqual(l.level, logging.WARNING)
    
    def test_manipulate_loggers(self):
        l = logging.getLogger("test")
        h = logging.StreamHandler()
        l.addHandler(h)
        self.assertIn(h, l.handlers)
        self.assertIsNone(logging.setLoggers())
        self.assertIsNone(logging.setLogger("test"))
        self.assertNotIn(h, l.handlers)
        f_with_logging(self, logger=logging.getLogger("other"))
        LoggingInFunc().f1(self)
        LoggingInFunc().f2(self, logger=logging.getLogger("other"))
        logging.renameLogger("test", "test2")
        self.assertEqual(l.name, "test2")
        self.assertRaises(ValueError, logging.renameLogger, "test", "test2")
        self.assertRaises(ValueError, logging.renameLogger, "test2", "test2")
        self.assertRaises(ValueError, logging.unsetLogger, "test")
        l2 = logging.getLogger("test3")
        l2.parent = l
        self.assertRaises(ValueError, logging.unsetLoggers, "test2")
        self.assertIsNone(logging.unsetLogger("test2", force=True))
        k = list(logging.root.manager.loggerDict.keys())
        self.assertNotIn("test", k)
        self.assertNotIn("test2", k)
        self.assertIn("test3", k)
    
    def test_std_to_logger(self):
        l = logging.getLogger("test")
        l.setLevel(logging.INFO)
        stdout = sys.stdout
        sys.stdout = logging.Std2Logger(l, "DEBUG")
        print("TEST")
        sys.stdout.flush()
        sys.stdout = stdout

