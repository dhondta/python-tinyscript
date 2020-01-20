# -*- coding: UTF-8 -*-
"""Common Python2/3 compatibility functions.

"""
from six import b as six_b, ensure_str as six_ensure_str, string_types, u

from .constants import PYTHON3


__all__ = __features__ = ["b", "byteindex", "execfile", "ensure_str",
                          "iterbytes", "string_types", "u"]


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
        pass
    try:
        return text.encode()
    except:
        return text


def ensure_str(text):
    """
    Ugly overload for six.ensure_str function, in order to avoir unicode error
     with the original one. 
    """
    try:
        return six_ensure_str(text)
    except:
        return text.decode("latin-1")


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
