#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module containing various helper functions.

"""
from .datatrans import *
from .licenses import *
from .patch import *
from .termsize import *
from .types import *
from .utils import *

from .datatrans import __features__ as _datatrans
from .licenses import __features__ as _licenses
from .patch import __features__ as _patch
from .termsize import __features__ as _termsize
from .types import __features__ as _types
from .utils import __features__ as _utils


__all__ = __features__ = _datatrans + _licenses + _patch + _termsize + \
                         _types + _utils
