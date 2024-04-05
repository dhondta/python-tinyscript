# -*- coding: UTF-8 -*-
"""Formerly common Python2/3 compatibility functions, now left for backward-compatibility.

"""
__all__ = __features__ = ["b", "binary_type", "byteindex", "execfile", "ensure_binary", "ensure_str", "iterbytes",
                          "reduce", "string_types", "text_type", "u"]


binary_type = bytes
integer_types = (int, )
string_types = (str, )
text_type = u = str

# see: http://python3porting.com/problems.html
byteindex = lambda d, i=None: d[i]


def b(s):
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
    if isinstance(s, str):
        return s.encode(encoding, errors)
    elif isinstance(s, bytes):
        return s
    else:
        raise TypeError("not expecting type '%s'" % type(s))


def ensure_str(s, encoding='utf-8', errors='strict'):
    if isinstance(s, bytes):
        try:
            return s.decode(encoding, errors)
        except:
            return s.decode("latin-1")
    elif not isinstance(s, (str, bytes)):
        raise TypeError("not expecting type '%s'" % type(s))
    return s


def execfile(source, globals=None, locals=None):
    with open(source) as f:
        content = f.read()
    exec(content, globals, locals)


def iterbytes(text):
    """ Bytes iterator. If a string is provided, it will automatically be converted to bytes. """
    if isinstance(text, str):
        text = b(text)
    for c in text:
        yield c


_initial_missing = object()

def reduce(function, sequence, initial=_initial_missing, stop=None):
    """ Similar to functools.reduce, but with a stop condition.
    reduce(function, sequence[, initial, stop]) -> value """
    it = iter(sequence)
    try:
        value = next(it) if initial is _initial_missing else initial
    except StopIteration:
        raise TypeError("reduce() of empty sequence with no initial value") from None
    for element in it:
        v = function(value, element)
        if stop and stop(v):
            break
        value = v
    return value

