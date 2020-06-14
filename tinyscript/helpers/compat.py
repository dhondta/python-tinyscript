# -*- coding: UTF-8 -*-
"""Common Python2/3 compatibility functions.

"""
from six import binary_type, string_types, text_type, u

from .constants import PYTHON3


__all__ = __features__ = ["b", "binary_type", "byteindex", "execfile", "ensure_binary", "ensure_str", "ensure_unicode",
                          "iterbytes", "string_types", "text_type", "u"]


# see: http://python3porting.com/problems.html
byteindex = lambda d, i=None: d[i] if PYTHON3 else ord(d[i])
ensure_unicode = text_type


def b(s):
    """
    Similar to six.b function, because the behavior of 'b' in Python2/3 is not exactly the same. This makes 'b' behave
     in Python 3 like in Python 2.
    """
    if PYTHON3:
        try:
            return s.encode("latin-1")
        except:
            pass
        try:
            return s.encode("utf-8")
        except:
            pass
    return s


def ensure_binary(s, encoding='utf-8', errors='strict'):
    """
    Identical to six.ensure_binary. Copied here to avoid messing up with six version errors.
    """
    if isinstance(s, text_type):
        return s.encode(encoding, errors)
    elif isinstance(s, binary_type):
        return s
    else:
        raise TypeError("not expecting type '%s'" % type(s))


def ensure_str(s, encoding='utf-8', errors='strict'):
    """
    Similar to six.ensure_str. Adapted here to avoid messing up with six version errors.
    """
    if not PYTHON3 and isinstance(s, text_type):
        return s.encode(encoding, errors)
    elif PYTHON3 and isinstance(s, binary_type):
        try:
            return s.decode(encoding, errors)
        except:
            return s.decode("latin-1")
    elif not isinstance(s, (text_type, binary_type)):
        raise TypeError("not expecting type '%s'" % type(s))
    return s


def execfile(source, globals=None, locals=None):
    with open(source) as f:
        content = f.read()
    exec(content, globals, locals)
if PYTHON3:
    __all__ += ["execfile"]


def iterbytes(text):
    """
    Bytes iterator. If a string is provided, it will automatically be converted to bytes.
    """
    if isinstance(text, string_types):
        text = b(text)
    for c in text:
        yield c if PYTHON3 else ord(c)

