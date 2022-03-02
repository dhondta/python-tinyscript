# -*- coding: UTF-8 -*-
"""Tinyscript package information.

"""
import os
from datetime import date

__author__    = "Alexandre D'Hondt"
__email__     = "alexandre.dhondt@gmail.com"
__copyright__ = "© 2017-%d A. D'Hondt" % date.today().year
__license__   = "gpl-3.0"

with open(os.path.join(os.path.dirname(__file__), "VERSION.txt")) as f:
    __version__ = f.read().strip()

