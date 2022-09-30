#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Expression evaluation functions' tests.

"""
from tinyscript.helpers.expressions import *
from tinyscript.helpers.expressions import BL_BUILTINS

from utils import TestCase


EXPRESSIONS = [
    "True",
    "[x for x in '123']",
    "list(x for x in [1,2,3])",
]


class TestHelpersExpressions(TestCase):
    def test_ast_nodes_evaluation(self):
        self.assertIsNotNone(eval_ast_nodes(*EXPRESSIONS))
    
    def test_expression_evaluations(self):
        # simple expresions (including list comprehensions and generators)
        for e in EXPRESSIONS:
            self.assertIsNotNone(eval2(e))
        # missing names
        self.assertIsNotNone(eval2("test + 1", {'test': 1}))
        self.assertRaises(NameError, eval2, "test + 1")
        # native blacklist of names
        for n in BL_BUILTINS:
            try:
                self.assertRaises(NameError, eval2, "%s('True')" % n)
            except SyntaxError:
                pass  # occurs with n="exec" under Python 2
        # code objects
        self.assertRaises(TypeError, eval2, "test", {'test': compile("None", "<string>", "exec")})
        # common attacks (triggers ValueError: node 'Attribute' is not allowed)
        self.assertRaises(ValueError, eval2, "__import__('subprocess').getoutput('id')")
        self.assertRaises(ValueError, eval2, "().__class__.__base__.__subclasses__()")

    def test_free_variables_evaluation(self):
        self.assertEqual(eval_free_variables("test + 1", **{'test': 1}), [])
        self.assertEqual(eval_free_variables(EXPRESSIONS[1]), ["x"])

