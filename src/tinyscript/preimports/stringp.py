# -*- coding: UTF-8 -*-
"""Module for enhancing string preimport.

"""
import re
import string

from ..helpers.termsize import get_terminal_size


def _natural_key(text):
    """ Key computation function for considering keys in a natural way.
    
    :param text: text to be used for computing the key
    """
    tokens = []
    for s in re.split(r"(\d+|\D+)", text):
        tokens.append(int(s) if s.isdigit() else s.lower())
    return tokens
string.natural_key = _natural_key


def sort_natural(strings):
    """ Simple function to sort a list of strings with numbers inside.
    
    :param strings: list of strings
    """
    strings.sort(key=_natural_key)
string.sort_natural = sort_natural


def sorted_natural(lst):
    """ Simple function to return a sorted list of strings with numbers inside.
    
    :param strings: list of strings
    :return:        list of strings sorted based on numbers inside
    """
    return sorted(lst, key=_natural_key)
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

