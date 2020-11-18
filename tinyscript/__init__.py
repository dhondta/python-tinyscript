#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Initialization of Tinyscript package.

"""

from .__info__ import __author__, __copyright__, __license__, __version__

from .features import *
from .helpers import *
from .parser import *
from .preimports import *
from .warnings import *

from .features import __features__ as _features
from .helpers import __features__ as _helpers
from .parser import __features__ as _parser
from .preimports import __features__ as _preimports
from .warnings import __features__ as _warnings


ts.__author__    = __author__
ts.__copyright__ = __copyright__
ts.__license__   = __license__
ts.__version__   = __version__


__all__ = _features + _helpers + _parser + _preimports + _warnings

