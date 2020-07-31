# -*- coding: UTF-8 -*-
"""Module for defining the list of preimports.

"""
import codext
from importlib import import_module
try:  # will work in Python 3
    from importlib import reload
    import configparser
except ImportError:  # will fail in Python 2 ; it will keep the built-in reload
    reload = reload
    import ConfigParser as configparser

from .codep import code
from .ftools import functools
from .hash import hashlib
from .inspectp import inspect
from .itools import itertools
from .log import logging
from .rand import random
from .regex import re
from .stringp import string
from .venv import virtualenv, PipPackage, VirtualEnv


__all__ = __features__ = ["PipPackage", "VirtualEnv", "import_module"]
__all__ += ["__imports__", "load", "reload"]

__imports__ = {
    'bad': [],
    'enhanced': [
        "code",
        "functools",
        "hashlib",
        "inspect",
        "itertools",
        "logging",
        "random",
        "re",
        "string",
        "virtualenv",
    ],
    'standard': [
        "argparse",
        "ast",
        "base64",
        "binascii",
        "codecs",
        "collections",
        "colorful",
        "configparser",
        "ctypes",
        "fileinput",
        "os",
        "platform",
        "shutil",
        "signal",
        "string",
        "struct",
        "subprocess",
        "sys",
        "time",
        "types",
        "uuid",
    ],
    'optional': [
        "bs4",
        "fs",
        "loremipsum",
        "requests",
    ]
}


def _load_preimports(*extras):
    """
    This loads the list of modules to be preimported in the global scope.
    
    :param extra: additional modules
    :return:      list of successfully imported modules, list of failures
    """
    i = __imports__
    for module in i['standard'] + i['enhanced'] + list(extras):
        load(module)
    for module in i['optional']:
        load(module, True)


def load(module, optional=False):
    """
    This loads a module and, in case of failure, appends it to a list of bad
     imports or not if it is required or optional.
    
    :param module:   module name
    :param optional: whether the module is optional or not
    """
    global __features__, __imports__
    m = globals().get(module)
    if m is not None:  # already imported (e.g. configparser)
        __features__.append(module)
        return m
    try:
        globals()[module] = m = import_module(module)
        m.__name__ = module
        __features__.append(module)
        return m
    except ImportError:
        if not optional and module not in __imports__['bad']:
            __imports__['bad'].append(module)
            for k, l in __imports__.items():
                if k != 'bad' and module in l:
                    l.remove(module)


_load_preimports()

