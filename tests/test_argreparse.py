#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Argreparse module assets' tests.

"""
from tinyscript.argreparse import ArgumentParser, Namespace
from utils import *


class TestArgreparse(TestCase):
    def setUp(self):
        self.argv = sys.argv[1:]  # backup input arguments
    
    def tearDown(self):
        sys.argv[1:] = self.argv  # restore input arguments

    def test_argument_parser(self):
        temp_stdin(self, "input_test")
        temp_stdout(self)
        sys.argv[1:] = []
        parser = ArgumentParser()
        parser.add_argument("test")
        parser.add_argument("--opt1")
        parser.add_subparsers().add_parser("subtest", help="test")
        sys.argv += ["--opt1", "test"]
        parser.add_argument("--opt2", action="store_true")
        sys.argv += ["--opt2"]
        parser.add_argument("-e", dest="ext", action="extend")
        sys.argv += ["-e", "1", "-e", "2", "-e", "3"]
        for _ in parser._sorted_actions():
            parser._set_arg(_)
        args = parser.parse_args()
        self.assertEqual(args.test, "input_test")
        self.assertEqual(args.opt1, "test")
        self.assertEqual(args.opt2, True)
        self.assertEqual(args.ext, ["1", "2", "3"])
    
    def test_parser_error(self):
        temp_stdout(self)
        sys.argv[1:] = []
        parser = ArgumentParser()
        parser.add_argument("test")
        self.assertRaises(SystemExit, parser.parse_args)
    
    def test_parser_conflicts(self):
        temp_stdout(self)
        sys.argv[1:] = []
        parser = ArgumentParser()
        parser.add_argument("--test", dest="verbose")
        parser.parse_args()
        parser.add_argument("-v", "--verbose", cancel=True)
        parser.parse_args()
    
    def test_namespace(self):
        ArgumentParser.reset()
        parser = ArgumentParser()
        ns = Namespace(parser)
        setattr(ns, "_hidden", "hidden")
        setattr(ns, "name", "shown")
        self.assertEqual(ns._hidden, "hidden")
        self.assertNotIn("hidden", str(ns))
        self.assertEqual(ns.name, "shown")
        self.assertIn("shown", str(ns))
        self.assertEqual(ns._collisions, {})
        o = parser._config.options("main")
        self.assertIn("_hidden", o)
        self.assertIn("name", o)
        self.assertNotIn("_collisions", o)
