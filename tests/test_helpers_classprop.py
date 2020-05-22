#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Classproperty tests.

"""
from tinyscript.helpers.classprop import *

from utils import TestCase


class UselessClass(object):
    _val1 = None
    
    def __init__(self):
        self._val2 = None
    
    @classproperty
    def val1(cls):
        return cls._val1
    
    @val1.setter
    def val1(cls, value):
        cls._val1 = value
    
    @property
    def val2(self):
        return self._val2

    @val2.setter
    def val2(self, value):
        self._val2 = value
    
    @classproperty
    @classmethod
    def val3(cls):
        return cls._val1


class TestHelpersClassProp(TestCase):
    def test_classproperty_feature(self):
        S1, S2, S3 = "OK1", "OK2", "OK3"
        self.assertIsNone(UselessClass.val1)
        self.assertIsNone(UselessClass.val3)
        self.assertIsInstance(UselessClass.val2, property)
        UselessClass.val1 = S1
        self.assertEqual(UselessClass.val1, S1)
        t1 = UselessClass()
        self.assertIsNone(t1.val2)
        t1.val2 = S2
        self.assertEqual(t1.val2, S2)
        self.assertIsInstance(UselessClass.val2, property)
        t1.val1 = S2
        self.assertEqual(t1.val1, S2)
        self.assertEqual(UselessClass.val1, S1)
        t2 = UselessClass()
        t2.val2 = S3
        self.assertEqual(t2.val2, S3)
        t2.val1 = S2
        self.assertEqual(t2.val1, S2)
        self.assertEqual(UselessClass.val1, S1)

