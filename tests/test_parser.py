#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Parser module assets' tests.

"""
from tinyscript import *
from tinyscript.parser import *
from tinyscript.parser import _save_config, ProxyArgumentParser
from utils import capture, remove, tmpf, TestCase


__examples__ = ["-v"]

INI = tmpf(ext="ini")


class TestParser(TestCase):
    @classmethod
    def setUpClass(cls):
        # collect ProxyArgumentParser object reference from the scope of
        #  tinyscript to reuse it afterwards (as it will be overwritten with the
        #  reference of a real parser each time initialize(...) is called)
        global proxy_parser
        proxy_parser = parser
    
    def setUp(self):
        global parser
        self.argv = sys.argv[1:]  # backup input arguments
        parser = proxy_parser     # reuse the original proxy parser reference
        parser.reset()
    
    def tearDown(self):
        sys.argv[1:] = self.argv  # restore input arguments
    
    def test_string_argument(self):
        sys.argv[1:] = ["--arg1", "test"]
        parser.add_argument("-a", "--arg1")
        initialize(globals())
        self.assertRaises(AttributeError, getattr, args, "does_not_exist")
        self.assertEqual(args.arg1, "test")
    
    def test_boolean_argument(self):
        sys.argv[1:] = ["-b"]
        parser.add_argument("-b", "--boolean", action="store_true")
        initialize(globals())
        self.assertEqual(args.boolean, True)
    
    def test_arg_name_clash(self):
        sys.argv[1:] = []
        parser.add_argument("-v", dest="v_opt_overwritten")
        initialize(globals())
        self.assertEqual(args.v_opt_overwritten, None)
    
    def test_initialization_flags(self):
        sys.argv[1:] = []
        initialize(globals(), False, *([True] * 9))
        self.assertFalse(args.interact)
        self.assertFalse(args.relative)
        self.assertFalse(args.stats)
        self.assertFalse(args.step)
        self.assertFalse(args.syslog)
        self.assertFalse(args.timings)
        self.assertEqual(args.verbose, 0)
        self.assertIs(args.logfile, None)
    
    def test_write_config(self):
        sys.argv[1:] = ["--arg1", "test", "--arg2", "-w", INI]
        parser.add_argument("-a", "--arg1")
        parser.add_argument("-b", "--arg2", action="store_true")
        initialize(globals(), add_config=True)
        _save_config(globals())
        with open(INI) as f:
            ini = f.read().strip()
        self.assertIn("arg1", ini)
        self.assertIn("arg2", ini)
    
    def test_read_config(self):
        sys.argv[1:] = ["-r", INI]
        parser.add_argument("-a", "--arg1")
        parser.add_argument("-b", "--arg2", action="store_true")
        with capture() as (out, err):
            initialize(globals(), add_config=True)
        self.assertEqual(args.arg1, "test")
        self.assertTrue(args.arg2)
        remove(INI)
    
    def test_noargs_action(self):
        sys.argv[1:] = []
        initialize(globals(), noargs_action="demo")
        with capture() as (out, err):
            logger.debug("test")
        self.assertIn("test", err.getvalue())
