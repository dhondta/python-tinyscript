#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Initialization of Tinyscript package.

"""
# NB: disabled as too expensive to load while almost not used ; if the error mentioned hereafter appears again, this
#      will be addressed in a different way
# this avoids an AssertionError due to pip being loaded before setuptools ;
#  see https://github.com/pypa/setuptools/issues/3044
#import setuptools

from warnings import filterwarnings
filterwarnings("ignore", "Setuptools is replacing distutils.")


from .__info__ import __author__, __copyright__, __license__, __version__

from .deprecation import *
from .features import *
from .helpers import *
from .parser import *
from .preimports import *

from .deprecation import __features__ as _deprecation
from .features import __features__ as _features
from .helpers import __features__ as _helpers
from .parser import __features__ as _parser
from .preimports import __features__ as _preimports


ts.__author__    = __author__
ts.__copyright__ = __copyright__
ts.__license__   = __license__
ts.__version__   = __version__


__all__ = _deprecation + _features + _helpers + _parser + _preimports

