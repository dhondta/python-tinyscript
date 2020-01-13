# -*- coding: UTF-8 -*-
"""Common Python2/3 compatibility functions.

"""
from six import b as six_b, string_types, u

from .constants import PYTHON3


__all__ = __features__ = ["b", "byteindex", "execfile", "iterbytes", "u"]


# see: http://python3porting.com/problems.html
byteindex = lambda d, i=None: d[i] if PYTHON3 else ord(d[i])


def b(text):
    """
    Overload for six.b function, because the behavior of 'b' in Python2/3 is not
     exactly the same. This makes 'b' behave in Python 3 like in Python 2.
    """
    try:
        return six_b(text)
    except:
        return text


def execfile(source, globals=None, locals=None):
    with open(source) as f:
        content = f.read()
    exec(content, globals, locals)
if PYTHON3:
    __all__ += ["execfile"]


def iterbytes(text):
    """
    Bytes iterator. If a string is provided, it will automatically be converted
     to bytes.
    """
    if isinstance(text, string_types):
        text = b(text)
    for c in text:
        yield c if PYTHON3 else ord(c)
