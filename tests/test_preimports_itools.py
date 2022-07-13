#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports iteration tools assets' tests.

"""
from tinyscript.preimports import itertools

from utils import *


@itertools.resettable
def gen1():
    yield "1"
    yield "2"


def gen2():
    yield "test"


class TestPreimportsItertools(TestCase):
    def test_lazy_product(self):
        g = gen1()
        self.assertEqual(len(list(itertools.product2("ab", g, repeat=2))), 16)
        self.assertEqual(len(list(itertools.product2("ab", g, g, g))), 16)
        self.assertRaises(ValueError, list, itertools.product2("ab", repeat=-1))
    
    def test_resettable_generator(self):
        self.assertRaises(ValueError, itertools.resettable, dummy_function)
        g1, g2 = gen1(), gen2()
        for i in range(10):
            self.assertEqual(next(g1), "1")
            self.assertEqual(next(g1), "2")
            self.assertRaises(StopIteration, next, g1)
            self.assertRaises(StopIteration, next, g1)
            g1 = itertools.reset(g1)
        self.assertRaises(itertools.NonResettableGeneratorException, itertools.reset, g2)

