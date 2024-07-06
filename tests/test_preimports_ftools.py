# -*- coding: UTF-8 -*-
"""Preimports code manipulation assets' tests.

"""
from tinyscript.preimports import functools

from utils import *


class TestPreimportsCode(TestCase):
    def test_class_wrapper(self):
        # source: https://stackoverflow.com/questions/6394511/python-functools-wraps-equivalent-for-classes
        @functools.wraps_cls
        class Memoized:
            def __init__(self, func):
                super().__init__()
                self.__func, self.__cache = func, {}
            def __call__(self, *args):
                try:
                    return self.__cache[args]
                except KeyError:
                    self.__cache[args] = v = self.__func(*args)
                    return v
                except TypeError:
                    return self.__func(*args)
            def __get__(self, obj, objtype):
                return functools.partial(self.__call__, obj)
        
        @Memoized
        def fibonacci(n):
            """fibonacci docstring"""
            if n in (0, 1):
               return n
            return fibonacci(n-1) + fibonacci(n-2)
        
        self.assertEqual(fibonacci.__doc__, "fibonacci docstring")
        self.assertIn("wrapper.<locals>.fibonacci", repr(fibonacci))

