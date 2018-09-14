#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common help utility functions.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["bin2int", "bin2txt", "int2bin", "txt2bin",
           "is_int", "is_lst", "is_str",
           "is_bin", "is_hex"]


from six import string_types


bin2int = lambda b: int("0b" + b, 2)
bin2txt = lambda b: ''.join(chr(bin2int(''.join(map(str, b[i:i+8])))) \
                    for i in range(0, len(b), 8))
int2bin = lambda i, n=None: ("{}" if n is None else "{:0>" + str(n) + "}") \
                            .format(bin(i)[2:])
txt2bin = lambda t: ''.join(map(lambda c: "{:0>8}".format(bin(ord(c))[2:]), t))

is_int = lambda i: isinstance(i, int)
is_lst = lambda l: isinstance(l, (list, tuple))
is_str = lambda s: isinstance(s, string_types)

is_bin = lambda b: (is_str or is_lst) and all(str(_) in "01" for _ in b)
is_hex = lambda h: is_str and len(h) % 2 == 0 and \
                   all(_ in "0123456789abcdef" for _ in h.lower())
