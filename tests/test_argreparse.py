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

    def test_positional_arguments(self):
        temp_stdout(self)
        temp_stdin(self, "input_test")
        sys.argv[1:] = []
        parser = ArgumentParser()
        parser.add_argument("test")
        for _ in parser._sorted_actions():
            parser._set_arg(_)
        args = parser.parse_args()
        self.assertEqual(args.test, "input_test")

    def test_optional_arguments(self):
        temp_stdout(self)
        sys.argv[1:] = []
        parser = ArgumentParser()
        parser.add_subparsers().add_parser("subtest", help="test")
        parser.add_argument("--opt1")
        sys.argv += ["--opt1", "test"]
        parser.add_argument("--opt2", action="store_true")
        sys.argv += ["--opt2"]
        parser.add_argument("-e", dest="ext", action="extend")
        sys.argv += ["-e", "1", "-e", "2", "-e", "3"]
        if PYTHON3:
            args = parser.parse_args()
            self.assertEqual(args.opt1, "test")
            self.assertEqual(args.opt2, True)
            self.assertEqual(args.ext, ["1", "2", "3"])
        else:
            self.assertRaises(SystemExit, parser.parse_args)
    
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
