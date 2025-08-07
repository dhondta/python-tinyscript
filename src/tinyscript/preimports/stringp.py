# -*- coding: UTF-8 -*-
"""Module for enhancing string preimport.

"""
import re
import string
from functools import wraps

from ..helpers.termsize import get_terminal_size


def _natural_key(case_sensitive=False):
    """ Key computation function for considering keys in a natural way.
    
    :param text: text to be used for computing the key
    """
    def _wrapper(text):
        return [(0, int(t)) if t.isdigit() else (1, t if case_sensitive else t.lower()) for t in \
                re.split(r"(\d+|\D+)", text)]
    return _wrapper
string.natural_key = _natural_key


def sort_natural(strings, case_sensitive=False):
    """ Simple function to sort a list of strings with numbers inside.
    
    :param strings: list of strings
    """
    strings.sort(key=_natural_key(case_sensitive))
string.sort_natural = sort_natural


def sorted_natural(lst, case_sensitive=False):
    """ Simple function to return a sorted list of strings with numbers inside.
    
    :param strings: list of strings
    :return:        list of strings sorted based on numbers inside
    """
    return sorted(lst, key=_natural_key(case_sensitive))
string.sorted_natural = sorted_natural


def shorten(string, length=None, end="..."):
    """ Simple string shortening function for user-friendlier display.
    
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

