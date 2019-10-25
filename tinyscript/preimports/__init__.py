# -*- coding: UTF-8 -*-
"""Module for defining the list of preimports.

"""
from importlib import import_module
try:  # will work in Python 3
    from importlib import reload
    import configparser
except ImportError:  # will fail in Python 2 ; it will keep the built-in reload
    reload = reload
    import ConfigParser as configparser

from .hash import hashlib
from .venv import virtualenv, VirtualEnv


__all__ = __features__ = ["VirtualEnv"]
__all__ += ["__badimports__", "__optimports__", "__preimports__",
            "load", "reload"]

__badimports__ = []
__optimports__ = [
    "bs4",
    "fs",
    "numpy",
    "pandas",
    "requests",
]
__preimports__ = [
    "argparse",
    "ast",
    "base64",
    "binascii",
    "codecs",
    "collections",
    "configparser",
    "ctypes",
    "fileinput",
    "hashlib",
    "itertools",
    "logging",
    "os",
    "random",
    "re",
    "shutil",
    "signal",
    "string",
    "subprocess",
    "sys",
    "time",
    "virtualenv",
]


def _load_preimports(*extras):
    """
    This loads the list of modules to be preimported in the global scope.
    
    :param extra: additional modules
    :return:      list of successfully imported modules, list of failures
    """
    for module in __preimports__ + list(extras):
        load(module)
    for module in __optimports__:
        load(module, True)


def load(module, optional=False):
    """
    This loads a module and, in case of failure, appends it to a list of bad
     imports or not if it is required or optional.
    
    :param module:   module name
    :param optional: whether the module is optional or not
    """
    global __badimports__, __features__, __preimports__
    m = globals().get(module)
    if m:  # already imported (e.g. configparser)
        __features__.append(module)
        return m
    try:
        globals()[module] = m = import_module(module)
        m.__name__ = module
        __features__.append(module)
        return m
    except ImportError:
        if not optional and module not in __badimports__:
            __badimports__.append(module)


_load_preimports()
