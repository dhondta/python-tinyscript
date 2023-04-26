# -*- coding: UTF-8 -*-
"""Decorators for classes and methods.

"""
from functools import wraps
try:  # PYTHON3
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec

from ..preimports import logging, sys


__all__ = __features__ = ["applicable_to", "failsafe", "try_and_pass", "try_and_warn", "try_or_die"]


def __is_method(f):
    spec = getfullargspec(f)
    return len(spec.args) > 0 and spec.args[0] == "self"



def applicable_to(*classes):
    """ Class decorator for checking that a class is well inherited from any given parent class. Used in checking
         mixins' compatibility.

    :param classes: list of compatible parent bot classes
    """
    def _wrapper(cls):
        class NewClass(cls):
            def __init__(self, *args, **kwargs):
                self.__doc__ = cls.__doc__
                self.__name__ = cls.__name__
                valid = [c.__name__ for c in classes]
                if all(c not in self.__class__.__mro__ for c in classes):
                    msg = "This class is not compatible with the given parent classes ({})".format(", ".join(valid))
                    g = {'__name__': "__main__"}
                    exec("class IncompatibleClassError(Exception): pass", g)
                    raise g['IncompatibleClassError'](msg)
                super(NewClass, self).__init__(*args, **kwargs)
        return NewClass
    return _wrapper


def failsafe(f):
    """ Simple decorator for catching every exception and returning None. """
    def __fw(*a, **kw):
        try:
            return f(*a, **kw)
        except:
            return
    return __fw


def try_and_pass(exc=Exception):
    """ Decorator handling a try-except block that simply continue the execution with no message in case of failure.

    :param exc: exception class on which the error is thrown
    """
    def _try_and_pass(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exc:
                pass
        return wrapper
    return _try_and_pass


def try_and_warn(message=None, exc=Exception, trace=False, extra_info=""):
    """ Decorator handling a try-except block to log a warning and continue the execution.

    :param message:    message to be displayed when crashing
    :param exc:        exception class on which the error is thrown
    :param trace:      display exception traceback
    :param extra_info: class attribute name whose value is to be displayed as additional information
    """
    def _try_and_warn(f):
        @wraps(f)
        @logging.bindLogger
        def wrapper(*args, **kwargs):
            self = args[0] if len(args) > 0 and __is_method(f) else None
            try:
                return f(*args, **kwargs)
            except exc as e:
                l = getattr(self, "logger", None) or logger
                l.warning(str(e) if message is None else message)
                if trace:
                    l.exception(e)
                if extra_info != "" and hasattr(self, extra_info):
                    l.info(getattr(self, extra_info))
        return wrapper
    return _try_and_warn


def try_or_die(message=None, exc=Exception, trace=True, extra_info=""):
    """ Decorator handling a try-except block to log an error.

    :param message:    message to be displayed when crashing
    :param exc:        exception class on which the error is thrown
    :param trace:      display exception traceback
    :param extra_info: class attribute name whose value is to be displayed as additional information (only applies when
                        used with a method)
    """
    def _try_or_die(f):
        @wraps(f)
        @logging.bindLogger
        def wrapper(*args, **kwargs):
            self = args[0] if len(args) > 0 and __is_method(f) else None
            try:
                return f(*args, **kwargs)
            except exc as e:
                l = getattr(self, "logger", None) or logger
                l.critical(str(e) if message is None else message)
                if trace:
                    l.exception(e)
                if extra_info != "" and hasattr(self, extra_info):
                    l.info(getattr(self, extra_info))
                # if the decorated method is part of a context manager, close it with its __exit__ method and continue
                if hasattr(self, "__exit__"):
                    self.__exit__(*sys.exc_info())
                # stop execution
                sys.exit(1)
        return wrapper
    return _try_or_die

