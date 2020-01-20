# -*- coding: UTF-8 -*-
"""Decorators for classes and methods.

"""
from functools import update_wrapper, wraps
from sys import exc_info
try:  # PYTHON3
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec


__all__ = __features__ = ["applicable_to", "try_or_die", "try_and_pass",
                          "try_and_warn"]


class IncompatibleClassError(Exception):
    pass


def __is_method(f):
    spec = getfullargspec(f)
    return len(spec.args) > 0 and spec.args[0] == "self"



def applicable_to(*classes):
    """
    Class decorator for checking that a class is well inherited from any given
     parent class. Used in checking mixins' compatibility.

    :param classes: list of compatible parent bot classes
    """
    def _wrapper(cls):
        class NewClass(cls):
            def __init__(self, *args, **kwargs):
                self.__doc__ = cls.__doc__
                self.__name__ = cls.__name__
                valid = [c.__name__ for c in classes]
                if all(c not in self.__class__.__mro__ for c in classes):
                    msg = "This class is not compatible with the given parent" \
                          " classes ({})".format(", ".join(valid))
                    raise IncompatibleClassError(msg)
                super(NewClass, self).__init__(*args, **kwargs)
        return NewClass
    return _wrapper


def try_or_die(message, exc=Exception, extra_info=""):
    """
    Decorator handling a try-except block to log an error.

    :param message:    message to be displayed when crashing
    :param exc:        exception class on which the error is thrown
    :param extra_info: class attribute name whose value is to be displayed as
                        additional information (only applies when used with a
                        method)
    """
    def _try_or_die(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            self = args[0] if len(args) > 0 and __is_method(f) else None
            try:
                return f(*args, **kwargs)
            except exc as e:
                # try to get a logger from the current instance or from the
                #  global scope
                l = getattr(self, "logger", None) or globals().get('logger')
                if l is not None:
                    l.critical(message)
                    if extra_info != "" and hasattr(self, extra_info):
                        l.info(getattr(self, extra_info))
                # if the decorated method is part of a context manager, close it
                #  with its __exit__ method and continue
                if hasattr(self, "__exit__"):
                    self.__exit__(*exc_info())
                # re-raise the exception
                raise e
        return wrapper
    return _try_or_die


def try_and_pass(exc=Exception):
    """
    Decorator handling a try-except block that simply continue the execution
     with no message in case of failure.

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


def try_and_warn(message, exc=Exception, trace=False, extra_info=""):
    """
    Decorator handling a try-except block to log a warning and continue the
     execution.

    :param message:    message to be displayed when crashing
    :param exc:        exception class on which the error is thrown
    :param trace:      display exception traceback
    :param extra_info: class attribute name whose value is to be displayed as
                        additional information
    """
    def _try_and_warn(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            self = args[0] if len(args) > 0 and __is_method(f) else None
            try:
                return f(*args, **kwargs)
            except exc:
                # try to get a logger from the current instance or from the
                #  global scope
                l = getattr(self, "logger", None) or globals().get('logger')
                if l is not None:
                    l.warning(message)
                    if trace:
                        l.exception(exc)
                    if extra_info != "" and hasattr(self, extra_info):
                        l.info(getattr(self, extra_info))
        return wrapper
    return _try_and_warn
