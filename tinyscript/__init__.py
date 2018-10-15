#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Initialization of Tinyscript package.

"""

from .__info__ import __author__, __copyright__, __version__

from .handlers import *
from .helpers import *
from .loglib import *
from .parser import *
from .preimports import *

from .handlers import __features__ as _handlers
from .helpers import __features__ as _helpers
from .loglib import __features__ as _loglib
from .parser import __features__ as _parser
from .preimports import __features__ as _preimports


__all__ = _handlers + _helpers + _loglib + _parser + _preimports + ["new"]


def new():
    from os.path import dirname, join
    with open(join(dirname(__file__), "template.py")) as fin, \
         open("template.py", 'w') as fout:
        fout.write(fin.read())
