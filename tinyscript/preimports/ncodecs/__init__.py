# -*- coding: UTF-8 -*-
"""Module for enhancing codecs preimport.

"""
import os

from ._utils import codecs


for f in os.listdir(os.path.dirname(__file__)):
    if not f.endswith(".py") or f == "__init__.py":
        continue
    __import__(f[:-3], globals(), locals(), [], 1)
