# -*- coding: UTF-8 -*-
"""Module for enhancing string preimport.

"""
import string

from ..helpers.termsize import get_terminal_size


def shorten(string, length=None, end="..."):
    """
    Simple string shortening function for user-friendlier display.
    
    :param string: the string to be shortened
    :param length: maximum length of the string
    """
    if length is None:
        ts = get_terminal_size()
        length = ts[0] if ts is not None else 40
    if not isinstance(length, int):
        raise ValueError("Invalid length '{}'".format(length))
    return string if len(string) <= length else string[:length-len(end)] + end
string.shorten = shorten

