#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining the list of preimports.

"""
import importlib

from .__info__ import __author__, __copyright__, __version__


# modules to be pre-imported in the main script using tinyscript
PREIMPORTS = [
    "argparse",
    "base64",
    "binascii",
    "collections",
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


preimports = []
for module in PREIMPORTS:
    try:
        globals()[module] = importlib.import_module(module)
        preimports.append(module)
    except ImportError:
        pass


__all__ = __features__ = preimports
