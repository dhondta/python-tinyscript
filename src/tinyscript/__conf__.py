# -*- coding: UTF-8 -*-
"""Deprecation warnings, for use when no backward-compatibility provided.

"""
import builtins
import warnings
from importlib import import_module
from inspect import currentframe
from lazy_object_proxy import Proxy
from functools import wraps

warnings.filterwarnings("always")


def deprecate(old, new=None):
    def _warn(o, n):
        msg = "'%s' has been deprecated" % o
        if new is not None:
            msg += ", please use '%s' instead" % n
        warnings.warn(msg, DeprecationWarning)
    # react differently in function of the input
    if isinstance(old, type(lambda: 0)):
        n = old.__name__
        def _old(old):
            @wraps(old)
            def _wrapper(*a, **kw):
                _warn(n, new)
                return old(*a, **kw)
            return _wrapper
        currentframe().f_back.f_globals[n] = _old(old)
    else:
        _warn(old, new)


builtins.deprecate = deprecate
builtins.warn = warnings.warn

builtins.lazy_object = Proxy


def lazy_load_module(module, relative=None, alias=None, postload=None):
    """ Lazily load a module. """
    glob = currentframe().f_back.f_globals
    def _load():
        glob[alias or module] = m = import_module(*((module, ) if relative is None else ("." + module, relative)))
        m.__name__ = alias or module
        if postload is not None:
            postload(m)
        return m
    glob[alias or module] = m = Proxy(_load)
    return m
builtins.lazy_load_module = lazy_load_module


def lazy_load_object(name, load_func, postload=None):
    """ Lazily load an object. """
    glob = currentframe().f_back.f_globals
    def _load():
        glob[name] = o = load_func()
        try:
            o._instance = o
        except (AttributeError, TypeError):
            pass
        if postload is not None:
            postload(o)
        return o
    glob[name] = o = Proxy(_load)
    return o
builtins.lazy_load_object = lazy_load_object

