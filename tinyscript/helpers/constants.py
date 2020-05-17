# -*- coding: UTF-8 -*-
"""Common constants.

"""
import sys
from locale import getlocale
from platform import system


__all__ = __features__ = ["DARWIN", "LINUX", "WINDOWS"]
DARWIN  = system() == "Darwin"
LINUX   = system() == "Linux"
WINDOWS = system() == "Windows"

__all__ += ["ENCODING", "LANGUAGE"]
LANGUAGE, ENCODING = getlocale()

__all__ += ["IPYTHON", "JUPYTER", "JYTHON", "PYPY", "PYTHON3"]
JYTHON  = sys.platform.startswith("java")
PYPY    = hasattr(sys, "pypy_version_info")
PYTHON3 = sys.version_info > (3,)
IPYTHON = JUPYTER = True
try:
    __IPYTHON__
except NameError:
    IPYTHON = JUPYTER = False

