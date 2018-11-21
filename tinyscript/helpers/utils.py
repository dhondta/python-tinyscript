#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common utility functions.

"""
import re

from .lambdas import is_lambda
from ..__info__ import __author__, __copyright__, __version__


__all__ = __features__ = ["user_input"]


REGEX = re.compile(r'^\(([a-z0-9])\).*$', re.I)


def user_input(prompt="", choices=None, default=None, choices_str=""):
    """
    Python2/3-compatible input method handling choices and default value.
    
    :param prompt:  prompt message
    :param choices: list of possible choices or lambda function
    :param default: default value
    :return:        handled user input
    """
    if type(choices) in [list, tuple, set]:
        choices_str = " {%s}" % (choices_str or \
                                 '|'.join(list(map(str, choices))))
        m = list(map(lambda x: REGEX.match(x), choices))
        choices = [x.group(1).lower() if x else c for x, c in zip(m, choices)]
        _check = lambda v: v in choices
    elif is_lambda(choices):
        _check = choices
    else:
        _check = lambda v: True
    default_str = " [{}]".format(default) if default else ""
    prompt += "{}{}\n >> ".format(choices_str, default_str)
    try:
        user_input = raw_input(prompt).strip()
    except NameError:
        user_input = input(prompt).strip()
    if type(choices) in [list, tuple, set]:
        user_input = user_input.lower()
    if user_input == "" and default is not None and _check(default):
        return default
    if _check(user_input):
        return user_input if len(user_input) > 0 else None
