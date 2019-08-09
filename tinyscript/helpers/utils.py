#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common utility functions.

"""
import colorful
import re
import sys
from platform import system
from six import b as six_b, u, StringIO
from slugify import slugify
from sys import version_info

from .types import is_lambda
from ..__info__ import __author__, __copyright__, __version__


__all__ = __features__ = ["LINUX", "MACOS", "PYTHON3", "WINDOWS", "b",
                          "byteindex", "capture", "confirm", "iterbytes",
                          "pause", "silent", "slugify", "std_input", "u",
                          "user_input", "Capture"]


LINUX   = system() == "Linux"
MACOS   = system() == "Darwin"
WINDOWS = system() == "Windows"

PYTHON3      = version_info > (3,)
CHOICE_REGEX = re.compile(r'^\(([a-z0-9])\).*$', re.I)


# see: http://python3porting.com/problems.html
byteindex = lambda d, i=None: d[i] if PYTHON3 else ord(d[i])
iterbytes = lambda d: iter(d) if PYTHON3 else [ord(c) for c in d]
pause = lambda *a, **kw: std_input("Press Enter to continue", *a, **kw) or None


def b(text):
    """
    Overload for six.b function, because the behavior of 'b' in Python2/3 is not
     exactly the same. This makes 'b' behave in Python 3 like in Python 2.
    """
    try:
        return six_b(text)
    except:
        return text


class _Text(object):
    """
    Dummy Text class for storing StringIO's content before closing it.
    """
    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.text


class Capture(object):
    """
    Context manager for capturing stdout and stderr.
    """
    def __init__(self, out=sys.stdout, err=sys.stderr):
        # backup original output file handles
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        
    def __enter__(self):
        # create new file handles
        sys.stdout, sys.stderr = StringIO(), StringIO()
        self.stdout, self.stderr = _Text(), _Text()
        # return references of the dummy objects
        return self.stdout, self.stderr
    
    def __exit__(self, *args):
        # freeze stdout and stderr contents before closing the file handles,
        #  using the references previously returned by __enter__
        self.stdout.text = sys.stdout.getvalue().strip() 
        self.stderr.text = sys.stderr.getvalue().strip()
        # close current file handles
        sys.stdout.close()
        sys.stderr.close()
        # restore original output file handles
        sys.stdout, sys.stderr = self._stdout, self._stderr


def capture(f):
    """
    Decorator for capturing stdout and stderr.
    """
    def _wrapper(*a, **kw):
        with Capture() as (out, err):
            r = f(*a, **kw)
        return r, out.text, err.text
    return _wrapper


def confirm(style="bold"):
    """
    Ask for confirmation.
    """
    return user_input("Are you sure ?", ["(Y)es", "(N)o"], "n", style=style) \
           == "y"


def silent(f):
    """
    Decorator for silencing stdout and stderr.
    """
    def _wrapper(*a, **kw):
        with Capture():
            r = f(*a, **kw)
        return r
    return _wrapper


def std_input(prompt="", style=None, palette=None):
    """
    Very simple Python2/3-compatible input method handling prompt styling.
    
    :param prompt:  prompt message
    :param style:   colorful styling function, e.g. red_on_green (for green
                     foreground and red background colors)
    :param palette: dictionary for defining new styles
    """
    colorful.update_palette(palette or {})
    if style is not None:
        if isinstance(style, (list, tuple, set)):
            style = "_".join(style)
        prompt = getattr(colorful, style)(prompt)
    try:
        return raw_input(prompt).strip()
    except NameError:
        return input(prompt).strip()


def user_input(prompt="", choices=None, default=None, choices_str="",
               required=False, **kwargs):
    """
    Python2/3-compatible input method handling choices and default value.
    
    :param prompt:   prompt message
    :param choices:  list of possible choices or lambda function
    :param default:  default value
    :param required: make non-null user input mandatory
    :param kwargs:   keyword-arguments to be passed to std_input for styling
    :return:         handled user input
    """
    if type(choices) in [list, tuple, set]:
        choices = list(map(str, choices))
        choices_str = " {%s}" % (choices_str or \
                                 '|'.join(list(map(str, choices))))
        # consider choices of the form ["(Y)es", "(N)o"] ;
        #  in this case, we want the choices to be ['y', 'n'] for the sake of
        #  simplicity for the user
        m = list(map(lambda x: CHOICE_REGEX.match(x), choices))
        choices = [x.group(1).lower() if x else c for x, c in zip(m, choices)]
        # this way, if using ["Yes", "No"], choices will remain so
        _check = lambda v: v in choices
    elif is_lambda(choices):
        _check = choices
    else:
        _check = lambda v: True
    prompt += "{}{}\n".format(choices_str, [" [{}]".format(default), ""]\
                                           [default is None and required])
    user_input, first = None, True
    while not user_input:
        user_input = std_input(["", prompt][first] + " >> ", **kwargs)
        first = False
        if type(choices) in [list, tuple, set]:
            choices = list(map(lambda x: x.lower(), choices))
            user_input = user_input.lower()
        if user_input == "" and default is not None and _check(default):
            return str(default)
        if user_input != "" and _check(user_input):
            return user_input
        if not required:
            return
