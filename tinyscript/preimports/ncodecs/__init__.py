# -*- coding: UTF-8 -*-
"""Module for enhancing codecs preimport.

"""
import codecs
import os


for f in os.listdir(os.path.dirname(__file__)):
    if not f.endswith(".py") or f == "__init__.py":
        continue
    mname = f[:-3]
    __import__(mname, globals(), locals(), [], 1)
