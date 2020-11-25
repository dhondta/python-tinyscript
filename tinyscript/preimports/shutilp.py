# -*- coding: UTF-8 -*-
"""Module for enhancing shutil preimport.

"""
import os
import shutil


def which(program):
    """ Already exists in Python 3. This function is for compatibility with Python 2.

    :param program: program name
    :return:        path to the program
    """
    for p in os.environ['PATH'].split(os.path.pathsep):
        p = os.path.join(p, program)
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
if not hasattr(shutil, "which"):
    shutil.which = which

