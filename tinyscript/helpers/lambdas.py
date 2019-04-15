#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common help utility help functions.

"""
from six import string_types

from ..__info__ import __author__, __copyright__, __version__


__all__ = __features__ = []


# various common data conversion one-liners
__all__ += ["bin2int", "bin2txt", "int2bin", "txt2bin"]
bin2int = lambda b: int("0b" + b, 2)
bin2txt = lambda b, n=8: ''.join(chr(bin2int(''.join(map(str, b[i:i+n])))) \
                                 for i in range(0, len(b), n))
int2bin = lambda i, n=8: ("{:0>%i}" % n).format(bin(i)[2:])
txt2bin = lambda t, n=8: "".join(map(lambda c: ("{:0>%i}" % n) \
                                              .format(bin(ord(c))[2:])[-n:], t))

# various object type check functions
__all__ += ["is_int", "is_pos_int", "is_lst", "is_str", "is_lambda"]
is_int     = lambda i: isinstance(i, int)
is_pos_int = lambda i: is_int(i) and i >= 0
is_lst     = lambda l: isinstance(l, (list, tuple))
is_str     = lambda s: isinstance(s, string_types)
is_lambda = lambda l: isinstance(l, type(lambda:0)) and \
                      l.__name__ == (lambda:0).__name__

# various data format check functions
__all__ += ["is_bin", "is_hex"]
is_bin = lambda b: (is_str or is_lst) and all(str(_) in "01" for _ in b)
is_hex = lambda h: is_str and len(h) % 2 == 0 and \
                   all(_ in "0123456789abcdef" for _ in h.lower())

# some other common check function
__all__ += ["is_long_opt", "is_short_opt"]
is_long_opt  = lambda o: len(o) > 2 and o.startswith('--')
is_short_opt = lambda o: len(o) == 2 and o.startswith('-')
