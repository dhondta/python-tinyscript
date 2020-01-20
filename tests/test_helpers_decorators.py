#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Decorators' tests.

"""
from tinyscript.helpers.decorators import *
from tinyscript.helpers.decorators import IncompatibleClassError

from utils import *


class GoodClass(object):
    pass


class BadClass(object):
    pass


@applicable_to(GoodClass)
class TestMixin(object):
    pass


class Test1(GoodClass, TestMixin):
    test = "test"
    
    def __init__(self):
        self.logger = logger
    
    def __exit__(self, *args):
        pass
    
    @try_or_die("TRY_OR_DIE message", extra_info="test")
    def test1(self):
        raise Exception("something wrong happened")
    
    @try_and_pass()
    def test2(self):
        raise Exception("something wrong happened")
    
    @try_and_warn("TRY_OR_WARN message", trace=True, extra_info="test")
    def test3(self):
        raise Exception("something wrong happened")


@try_or_die("TRY_OR_DIE message", extra_info="test")
def test1(self):
    raise Exception("something wrong happened")

@try_and_pass()
def test2(self):
    raise Exception("something wrong happened")

@try_and_warn("TRY_OR_WARN message", trace=True, extra_info="test")
def test3(self):
    raise Exception("something wrong happened")


class Test2(BadClass, TestMixin):
    pass


class TestHelpersDecorators(TestCase):
    def test_applicable_to(self):
        self.assertIsNotNone(Test1())
        self.assertRaises(IncompatibleClassError, Test2)
    
    def test_try_decorators(self):
        temp_stdout(self)
        t = Test1()
        self.assertRaises(Exception, t.test1)
        self.assertIsNone(t.test2())
        self.assertIsNone(t.test3())
        self.assertRaises(Exception, test1)
        self.assertIsNone(test2())
        self.assertIsNone(test3())
