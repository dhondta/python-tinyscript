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
from .warnings import *

from .handlers import __features__ as _handlers
from .helpers import __features__ as _helpers
from .loglib import __features__ as _loglib
from .parser import __features__ as _parser
from .preimports import __features__ as __preimports__
from .warnings import __features__ as _warnings


__all__ = _handlers + _helpers + _loglib + _parser + __preimports__ + _warnings
