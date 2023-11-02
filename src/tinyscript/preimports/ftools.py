# -*- coding: UTF-8 -*-
"""Module for enhancing functools preimport.

"""
import functools


# source: https://stackoverflow.com/questions/6394511/python-functools-wraps-equivalent-for-classes
def wraps_cls(cls):
    """ functools.wraps equivalent for classes. """
    class _Wrapper(cls):
        def __init__(self, wrapped, assignents=functools.WRAPPER_ASSIGNMENTS):
            self.__wrapped__ = wrapped
            for attr in assignents:
                setattr(self, attr, getattr(wrapped, attr))
            super().__init__()
        
        def __repr__(self):
            return repr(self.__wrapped__)
    return _Wrapper
functools.wraps_cls = wraps_cls

