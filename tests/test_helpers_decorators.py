#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Decorators' tests.

"""
from tinyscript.helpers.decorators import *

from utils import *


class GoodClass(object):
    pass


class BadClass(object):
    pass


@applicable_to(GoodClass)
class EmptyMixin(object):
    pass


class UselessClass(GoodClass, EmptyMixin):
    test = "test"
    
    def __init__(self):
        self.logger = logger
    
    def __exit__(self, *args):
        pass
    
    @try_or_die("TRY_OR_DIE message", extra_info="test")
    def func1(self):
        raise Exception("something wrong happened")
    
    @try_and_pass()
    def func2(self):
        raise Exception("something wrong happened")
    
    @try_and_warn("TRY_OR_WARN message", trace=True, extra_info="test")
    def func3(self):
        raise Exception("something wrong happened")


@failsafe
def func():
    raise Exception("something wrong happened")


@try_or_die("TRY_OR_DIE message", extra_info="test")
def func1():
    raise Exception("something wrong happened")

@try_and_pass()
def func2():
    raise Exception("something wrong happened")

@try_and_warn("TRY_OR_WARN message", trace=True, extra_info="test")
def func3():
    raise Exception("something wrong happened")


class UselessClass2(BadClass, EmptyMixin):
    pass


class TestHelpersDecorators(TestCase):
    def test_applicable_to(self):
        self.assertIsNotNone(UselessClass())
        self.assertRaises(Exception, UselessClass2)
    
    def test_try_decorators(self):
        temp_stdout(self)
        t = UselessClass()
        self.assertRaises(SystemExit, t.func1)
        self.assertIsNone(t.func2())
        self.assertIsNone(t.func3())
        self.assertIsNone(func())
        #self.assertRaises(Exception, func1)
        self.assertIsNone(func2())
        self.assertIsNone(func3())

