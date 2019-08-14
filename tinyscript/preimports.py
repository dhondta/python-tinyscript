#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining the list of preimports.

"""
from importlib import import_module
from six import b
try:  # will work in Python 3
    from importlib import reload
except ImportError:  # will fail in Python 2 ; it will keep the built-in reload
    reload = reload

from .__info__ import __author__, __copyright__, __version__


__all__ = __features__ = []
__all__ += ["__badimports__", "__optimports__", "__preimports__",
            "load", "reload"]

__badimports__ = []
__optimports__ = [
    "fs",
    "numpy",
    "pandas",
]
__preimports__ = [
    "argparse",
    "base64",
    "binascii",
    "collections",
    "hashlib",
    "itertools",
    "logging",
    "os",
    "random",
    "re",
    "shutil",
    "signal",
    "string",
    "sys",
    "time",
]


def load(module, optional=False):
    """
    This loads a module and, in case of failure, appends it to a list of bad
     imports or not if it is required or optional.
    
    :param module:   module name
    :param optional: whether the module is optional or not
    """
    global __badimports__, __features__, __preimports__
    try:
        globals()[module] = m = import_module(module)
        m.__name__ = module
        __features__.append(module)
        return m
    except ImportError:
        if not optional and module not in __badimports__:
            __badimports__.append(module)


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
_load_preimports()


# hashlib improvements
def hash_file(filename, algo="sha256"):
    """
    This extends hashlib's hashing function to hash a file per block.

    :param filename: name of the file to be hashed
    :return:         ALGO(file)
    """
    h = hashlib.new(algo)
    with open(filename, 'rb') as f:
        while True:
            b = f.read(h.block_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()
hashlib.hash_file = hash_file


# this binds new file hashing functions to the hashlib for each existing hash
#  algorithm
for algo in [x for x in hashlib.__dict__.keys()]:
    try:
        h = hashlib.new(algo)  # this fails if the algo is not valid, then
        h.update(b(""))        #  excluding module objects that aren't hash
                               #  algorithm functions
        def _hash_file(a):
            def _wrapper(f):
                return hash_file(f, a)
            return _wrapper
        setattr(hashlib, "{}_file".format(algo), _hash_file(algo))
    except ValueError:  # triggered by h.update(b(""))
        pass
