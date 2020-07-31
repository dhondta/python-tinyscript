# -*- coding: UTF-8 -*-
"""Common constants.

"""
import sys
from getpass import getuser
from locale import getlocale
from platform import system


__all__ = __features__ = ["DARWIN", "LINUX", "WINDOWS"]
DARWIN  = system() == "Darwin"
LINUX   = system() == "Linux"
WINDOWS = system() == "Windows"

__all__ += ["ADMIN", "USER"]
USER = getuser()
ADMIN = USER == ["root", "Administrator"][WINDOWS]

__all__ += ["ENCODING", "LANGUAGE"]
LANGUAGE, ENCODING = getlocale()

__all__ += ["IPYTHON", "JUPYTER", "JYTHON", "PYPY", "PYTHON2", "PYTHON3", "TTY"]
JYTHON  = sys.platform.startswith("java")
PYPY    = hasattr(sys, "pypy_version_info")
PYTHON2 = sys.version_info < (3,)
PYTHON3 = sys.version_info > (3,)
TTY     = sys.stdout.isatty()
try:
    __IPYTHON__
    IPYTHON = JUPYTER = True
except NameError:
    IPYTHON = JUPYTER = False

