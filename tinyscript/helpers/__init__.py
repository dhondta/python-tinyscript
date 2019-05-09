#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module containing various helper functions.

"""
from .lambdas import *
from .licenses import *
from .patch import *
from .termsize import *
from .types import *
from .utils import *

from .lambdas import __features__ as _lambdas
from .licenses import __features__ as _licenses
from .patch import __features__ as _patch
from .termsize import __features__ as _termsize
from .types import __features__ as _types
from .utils import __features__ as _utils


__all__ = __features__ = _patch + _lambdas + _licenses + _termsize + _types + \
                         _utils
