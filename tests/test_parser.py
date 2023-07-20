#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Parser module assets' tests.

"""
from tinyscript import *
from tinyscript.parser import *
from tinyscript.parser import _save_config, ProxyArgumentParser

from utils import *


for k, v in FIXTURES.items():
    globals()[k] = v

INI = tmpf(ext="ini")
INI_CONF = """[main]
arg1 = test
arg2 = True"""


class TestParser(TestCase):
    @classmethod
    def setUpClass(cls):
        # collect ProxyArgumentParser object reference from the scope of tinyscript to reuse it afterwards (as it will
        #  be overwritten with the reference of a real parser each time initialize(...) is called)
        global proxy_parser
        proxy_parser = parser
        cls.argv = sys.argv[1:]  # backup input arguments
    
    @classmethod
    def tearDownClass(cls):
        sys.argv[1:] = cls.argv  # restore input arguments
    
    def setUp(self):
        global parser
        if '__docformat__' in globals():
            del globals()['__docformat__']
        parser = proxy_parser  # reuse the original proxy parser reference
    
    def test_input_arguments(self):
        sys.argv[1:] = ["--arg1", "test", "-b"]
        parser.add_argument("-a", "--arg1")
        parser.add_argument("-b", "--boolean", action="store_true")
        initialize()
        self.assertEqual(args.boolean, True)
        self.assertRaises(AttributeError, getattr, args, "does_not_exist")
        self.assertEqual(args.arg1, "test")
    
    def test_subparser(self):
        temp_stdout(self)
        sys.argv[1:] = ["subtest", "-b", "test"]
        test = parser.add_subparsers().add_parser("subtest", parents=[parser])
        test.add_argument("-b", "--arg2")
        if PYTHON3:
            initialize()
        else:  # with Python2, an error occurs with the overwritten sys.argv and "subtest" is not parsed, hence throwing
               #  SystemExit with code 2 as the subparser selection is missing
            self.assertRaises(SystemExit, initialize, globals())
    
    def test_argument_conflicts(self):
        sys.argv[1:] = []
        parser.add_argument("-v", dest="v_opt_overwritten")
        initialize()
        self.assertEqual(args.v_opt_overwritten, None)
        # default verbose option still exists as only "-v" was overwritten
        self.assertEqual(args.verbose, False)
    
    def test_help_message_variants(self):
        # multi-level help
        globals()['__details__'] = ["first level", "second level", "unused"]
        for i in range(1, 5):
            sys.argv[1:] = ["-{}".format(i * "h")]
            self.assertRaises(SystemExit, initialize)
        globals()['__details__'] = "single extra level"
        for i in range(1, 5):
            sys.argv[1:] = ["-{}".format(i * "h")]
            self.assertRaises(SystemExit, initialize)
        del globals()['__details__']
        # help's documentation formats
        globals()['__docformat__'] = "BAD"
        self.assertRaises(ValueError, initialize)
        for fmt in ["html", "md", "rst", "textile", None]:
            globals()['__docformat__'] = fmt
            parser.add_argument("--opt1")
            parser.add_argument("--opt2", action="store_true")
            sys.argv[1:] = ["--help"]
            self.assertRaises(SystemExit, initialize)
    
    def test_initialization_flags(self):
        sys.argv[1:] = ["--stats"]
        initialize(
            add_banner=False,
            add_config=False,
            add_demo=True,
            add_interact=True,
            add_progress=True,
            add_step=True,
            add_time=True,
            add_version=True,
            add_wizard=True,
            multi_level_debug=True,
            short_long_help=False,
            ext_logging=True,
        )
        self.assertFalse(args.interact)
        self.assertFalse(args.progress)
        self.assertFalse(args.relative)
        self.assertTrue(args.stats)
        self.assertFalse(args.step)
        self.assertFalse(args.syslog)
        self.assertFalse(args.timings)
        self.assertEqual(args.verbose, 0)
        self.assertIs(args.logfile, None)
        self.assertRaises(TypeError, initialize, bad_arg=True)
    
    def test_write_config(self):
        sys.argv[1:] = ["--arg1", "test", "--arg2", "-w", INI]
        parser.add_argument("-a", "--arg1")
        parser.add_argument("-b", "--arg2", action="store_true")
        initialize(add_config=True)
        _save_config(globals())
        with open(INI) as f:
            ini = f.read().strip()
        self.assertIn("arg1", ini)
        self.assertIn("arg2", ini)
        remove(INI)
    
    def test_read_config(self):
        temp_stdout(self)
        with open(INI, 'w') as f:
            f.write(INI_CONF)
        sys.argv[1:] = ["-r", INI]
        parser.add_argument("-a", "--arg1")
        parser.add_argument("-b", "--arg2", action="store_true")
        initialize(add_config=True)
        self.assertEqual(args.arg1, "test")
        self.assertTrue(args.arg2)
        remove(INI)
    
    def test_noargs_empty_config(self):
        temp_stdout(self)
        sys.argv[1:] = []
        # SystemExit is raised as the default "config.ini" does not exist
        self.assertRaises(SystemExit, initialize, noargs_action="config")
    
    def test_noargs_help(self):
        temp_stdout(self)
        sys.argv[1:] = []
        # SystemExit is raised with code 0 as the help message is displayed then it exits
        self.assertRaises(SystemExit, initialize, noargs_action="help")
    
    def test_noargs_interact(self):
        sys.argv[1:] = []
        initialize(noargs_action="interact")
        self.assertTrue(args.interact)
        self.assertEqual(str(args.host), "127.0.0.1")
        self.assertEqual(args.port, 12345)
    
    def test_noargs_notify(self):
        sys.argv[1:] = []
        initialize(noargs_action="notify")
        self.assertTrue(args.notify)
    
    def test_noargs_progress(self):
        sys.argv[1:] = []
        initialize(noargs_action="progress")
        self.assertTrue(args.progress)
    
    def test_noargs_step(self):
        sys.argv[1:] = []
        initialize(noargs_action="step")
        self.assertTrue(args.step)
    
    def test_noargs_time(self):
        sys.argv[1:] = []
        initialize(noargs_action="time")
        self.assertTrue(args.stats)
        self.assertFalse(args.timings)
    
    def test_noargs_usage(self):
        sys.argv[1:] = []
        # SystemExit is raised with code 0 as the usage is displayed then it exits
        with self.assertRaises(SystemExit):
            initialize(noargs_action="usage")
    
    def test_noargs_version(self):
        temp_stdout(self)
        sys.argv[1:] = []
        # SystemExit is raised with code 0 as the version is displayed then it exits
        with self.assertRaises(SystemExit):
            initialize(noargs_action="version")
    
    def test_noargs_wizard(self):
        temp_stdout(self)
        temp_stdin(self, "\n")
        sys.argv[1:] = []
        initialize(noargs_action="wizard")
    
    def test_noargs_action(self):
        sys.argv[1:] = []
        initialize(noargs_action="demo")
        # __examples__ = ["-v"]
        self.assertTrue(args.verbose)
    
    def test_bad_noargs_action(self):
        sys.argv[1:] = []
        with self.assertRaises(ValueError):
            initialize(noargs_action="does_not_exist")
    
    def test_scriptname_banner(self):
        sys.argv[1:] = []
        initialize(add_banner=True)
        gd = globals()
        gd['BANNER_FONT'] = "standard"
        initialize()
    
    def test_report_good_function(self):
        if PYTHON3:
            temp_stdout(self)
            sys.argv[1:] = []
            initialize(report_func=lambda: (Title("Test"), ))
            self.assertEqual(args.output, "pdf")
            self.assertIs(args.title, None)
            self.assertIs(args.css, None)
            self.assertEqual(args.theme, "default")
            self.assertIs(args.filename, None)
    
    def test_report_bad_function(self):
        if PYTHON3:
            temp_stdout(self)
            sys.argv[1:] = []
            initialize(report_func="bad report function")
            self.assertFalse(hasattr(args, "output"))
            self.assertFalse(hasattr(args, "title"))
            self.assertFalse(hasattr(args, "css"))
            self.assertFalse(hasattr(args, "theme"))
            self.assertFalse(hasattr(args, "filename"))

