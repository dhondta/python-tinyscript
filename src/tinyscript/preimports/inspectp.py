# -*- coding: UTF-8 -*-
"""Module for enhancing inspect preimport.

"""
import inspect
import sys


def getcallermodule():
    """ Return the module the caller belongs to. """
    return inspect.getmodule(inspect.currentframe().f_back)
inspect.getcallermodule = getcallermodule


def getmainframe():
    """ Return __main__'s frame object. """
    return getparentframe(__name__="__main__") or inspect.currentframe()
inspect.getmainframe = getmainframe


def getmainglobals():
    """ Return __main__'s globals. """
    return getmainframe().f_globals
inspect.getmainglobals = getmainglobals


def getmainmodule():
    """ Return __main__'s frame object. """
    return inspect.getmodule(getmainframe())
inspect.getmainmodule = getmainmodule


def getparentframe(**kwargs):
    """ Return the frame object of the first one having kwargs in its globals. """
    frame = inspect.stack()[0][0]
    while frame is not None:
        frame = frame.f_back
        if frame and all(frame.f_globals.get(k) == v for k, v in kwargs.items()):
            break
    return frame
inspect.getparentframe = getparentframe


if sys.version_info < (3,):
    def unwrap(func):
        """ Simple function to get the object wrapped by func. This is already implemented (more complex) in Python 3.
             This function is for compatibility with Python 2. """
        while hasattr(func, '__wrapped__') and func is not func.__wrapped__:
            func = func.__wrapped__
        return func
    inspect.unwrap = unwrap

