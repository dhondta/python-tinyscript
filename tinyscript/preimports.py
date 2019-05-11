#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining the list of preimports.

"""
import importlib
from six import b
try:
    reload = reload
except NameError:
    reload = importlib.reload

from .__info__ import __author__, __copyright__, __version__


# modules to be pre-imported in the main script using tinyscript
PREIMPORTS = [
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


def _load_preimports(*extras):
    """
    This loads the list of modules to be preimported in the global scope.
    
    :param extra: additional modules
    :return:      list of successfully imported modules, list of failures
    """
    preimports, failures = [], []
    for module in PREIMPORTS + list(extras):
        try:
            globals()[module] = importlib.import_module(module)
            preimports.append(module)
        except ImportError:
            failures.append(module)
    return preimports, failures
__preimports = _load_preimports()[0]


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


__all__ = __features__ = __preimports
__all__ += ["reload", "PREIMPORTS"]
