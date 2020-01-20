#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Classproperty tests.

"""
from tinyscript.helpers.classprop import *

from utils import TestCase


class Test(object):
    _test1 = None
    
    def __init__(self):
        self._test2 = None
    
    @classproperty
    def test1(cls):
        return cls._test1
    
    @test1.setter
    def test1(cls, value):
        cls._test1 = value
    
    @property
    def test2(self):
        return self._test2

    @test2.setter
    def test2(self, value):
        self._test2 = value
    
    @classproperty
    @classmethod
    def test3(cls):
        return cls._test1


class TestHelpersClassProp(TestCase):
    def test_classproperty_feature(self):
        S1, S2, S3 = "OK1", "OK2", "OK3"
        self.assertIsNone(Test.test1)
        self.assertIsInstance(Test.test2, property)
        Test.test1 = S1
        self.assertEqual(Test.test1, S1)
        t1 = Test()
        self.assertIsNone(t1.test2)
        t1.test2 = S2
        self.assertEqual(t1.test2, S2)
        self.assertIsInstance(Test.test2, property)
        t1.test1 = S2
        self.assertEqual(t1.test1, S2)
        self.assertEqual(Test.test1, S1)
        t2 = Test()
        t2.test2 = S3
        self.assertEqual(t2.test2, S3)
        t2.test1 = S2
        self.assertEqual(t2.test1, S2)
        self.assertEqual(Test.test1, S1)
