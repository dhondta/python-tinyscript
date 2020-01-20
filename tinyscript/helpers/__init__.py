# -*- coding: UTF-8 -*-
"""Module containing various helper functions.

"""
from pprint import pprint
from types import ModuleType

from .classprop import *
from .common import *
from .compat import *
from .constants import *
from .data import *
from .decorators import *
from .inputs import *
from .licenses import *
from .path import *
from .termsize import *
from .timeout import *

from .classprop import __features__ as _classprop
from .common import __features__ as _common
from .compat import __features__ as _compat
from .constants import __features__ as _constants
from .data import __features__ as _data
from .decorators import __features__ as _decorators
from .inputs import __features__ as _inputs
from .licenses import __features__ as _licenses
from .path import __features__ as _path
from .termsize import __features__ as _termsize
from .timeout import __features__ as _timeout


__helpers__ = _common + _data + _decorators + _inputs + _licenses + _path + \
              _termsize + _timeout

ts = ModuleType("ts", """
    Tinyscript helpers
    ~~~~~~~~~~~~~~~~~~

    The `ts` module contains various helper functions that can be very useful
     to not reinvent the wheel, including:
    
    - Common utility functions
    
      Bruteforce generator, customized with minimum and maximum lengths and an
      alphabet. A dummy process execution function is also available.
      
    - Data-related functions
    
      This encompasses argparse argument types and data transformation functions
      i.e. from and to bin/int/hex.
      
    - Useful decorators
    
      I.e. for trying something while choosing a different action if the
      execution fails (e.g. simply passing, warning the user or interrupting the
      program).
      
    - Input functions
      
      This relates to functions expecting user inputs like a 'pause' function,
      a 'confirm' function (with a customizable message and set of answers), a
      'user_input' function with styling, ...
      
    - Path-related helpers
      
      Some useful path functions, enhanced from pathlib.Path's one. It adds
      various methods to Path and provides helpers for mirroring a path or
      creating a temporary one.
      
    - Timeout items
      
      This provides a timeout decorator and a timeout context manager.
      
    - Others
    
      Namely license-related functions, terminal size get function, ...
""")
for h in __helpers__:
    setattr(ts, h, globals()[h])

__all__ = __features__ = ["pprint", "ts"] + _classprop + _compat + _constants
