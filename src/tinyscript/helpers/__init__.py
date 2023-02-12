# -*- coding: UTF-8 -*-
"""Module containing various helper functions.

"""
from pprint import pprint
from types import ModuleType

from .attack import *
from .classprop import *
from .common import *
from .compat import *
from .constants import *
from .data import *
from .decorators import *
from .dictionaries import *
from .docstring import *
from .expressions import *
from .fexec import *
from .inputs import *
from .layout import *
from .licenses import *
from .notify import *
from .password import *
from .path import *
from .termsize import *
from .text import *
from .timeout import *

from .attack import __features__ as _attack
from .classprop import __features__ as _clsprop
from .common import __features__ as _common
from .compat import __features__ as _compat
from .constants import __features__ as _csts
from .data import __features__ as _data
from .decorators import __features__ as _dec
from .dictionaries import __features__ as _dict
from .docstring import __features__ as _docs
from .expressions import __features__ as _expr
from .fexec import __features__ as _fexec
from .inputs import __features__ as _inputs
from .layout import __features__ as _layout
from .licenses import __features__ as _lic
from .notify import __features__ as _notify
from .password import __features__ as _pswd
from .path import __features__ as _path
from .termsize import __features__ as _tsize
from .text import __features__ as _text
from .timeout import __features__ as _to


__helpers__ = _attack + _common + _data + _dec + _dict + _docs + _expr + _fexec + _inputs + _layout + _lic + _notify + \
              _path + _pswd + _tsize + _text + _to

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
      
      Some useful path functions, enhanced from pathlib2.Path's one. It adds
      various methods to Path and provides helpers for mirroring a path or
      creating a temporary one.
      
    - Timeout items
      
      This provides a timeout decorator and a timeout context manager.
      
    - Others
    
      Namely license-related functions, terminal size get function, ...
""")
for h in __helpers__:
    setattr(ts, h, globals()[h])

__all__ = __features__ = ["colored", "pprint", "ts"] + _clsprop + _compat + _csts

