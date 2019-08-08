#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common help utility help functions.

"""
from six import string_types

from .types import is_bin, is_hex, is_int, is_neg_int, is_str
from ..__info__ import __author__, __copyright__, __version__


__all__ = __features__ = []


__all__ = __features__ = [
    "bin2int", "bin2hex", "bin2str",
    "hex2bin", "hex2int", "hex2str",
    "int2bin", "int2hex", "int2str",
    "str2bin", "str2int", "str2hex"
]


# BINARY STRING <=> HEXADECIMAL STRING
def bin2hex(binary_string, n_bits=8, n_groups=1, sep=None, order="little"):
    """ Convert a binary string (eventually using a separator) to a hexadecimal
         string, using a given number of bits and in little or big endian. """
    return int2hex(bin2int(binary_string, n_bits, n_groups, sep, order))


# BINARY STRING <=> INTEGER
def bin2int(binary_string, n_bits=8, n_groups=1, sep=None, order="little"):
    """ Convert a binary string (eventually using a separator) to an integer,
         using a given number of bits and in little or big endian. """
    b, n, m = binary_string, n_bits, n_groups
    # check for input arguments
    if not is_bin(b, sep):
        raise ValueError("Bad input binary string")
    if is_neg_int(n, zero=True):
        raise ValueError("Number of bits must be a positive integer")
    if order not in ["little", "big"]:
        raise ValueError("Bad bits group order")
    # pad with zeros to the left of the binary string
    if sep is None or sep == "":
        b = (n - len(b) % n) % n * "0" + b
    # split the binary string into groups
    bits_groups = [b[i:i+n] for i in range(0, len(b), n)] if sep is None else \
                  b.split(sep)
    # then process each block of n_groups groups according to the order
    r = []
    for i in range(0, len(bits_groups), m):
        groups = bits_groups[i:i+m]
        for group in (groups if order == "little" else groups[::-1]):
            if len(group) > n:
                raise ValueError("Bad input binary string")
            r.append(("{:0>%i}" % n).format(group))
    return int("0b" + "".join(r), 2)


# BINARY STRING <=> 8-BITS CHARACTERS
def bin2str(binary_string, n_bits=8, n_groups=1, sep=None, order="little"):
    """ Convert a binary string (eventually using a separator) to string of
         8-bits characters, using a given number of bits and in little or big
         endian. """
    return int2str(bin2int(binary_string, n_bits, n_groups, sep, order))


def hex2bin(hex_string, n_bits=8, n_groups=1, sep=None, order="little"):
    """ Convert a hexadecimal string to a binary string, using a given number of
         bits and in little or big endian. """
    return int2bin(hex2int(hex_string), n_bits, n_groups, sep, order)


# HEXADECIMAL STRING <=> INTEGER
def hex2int(hex_string):
    """ Convert a hexadecimal string to a big integer. """
    h = hex_string
    # check for input arguments
    if not is_hex(h):
        raise ValueError("Bad input hexadecimal string")
    return int(h, 16)


# HEXADECIMAL STRING <=> 8-BITS CHARACTERS
def hex2str(hex_string):
    """ Convert a hexadecimal string to a string of 8-bits characters. """
    return int2str(hex2int(hex_string))


# INTEGER <=> BINARY STRING
def int2bin(integer, n_bits=8, n_groups=1, sep=None, order="little"):
    """ Convert an integer to a binary string (eventually using a separator),
         using a given number of bits and in little or big endian. """
    n, m = n_bits, n_groups
    # check for input arguments
    if not is_int(integer):
        raise ValueError("Bad input integer")
    if not is_int(n) or is_neg_int(n, zero=True):
        raise ValueError("Number of bits must be a positive integer")
    if not is_int(n) or is_neg_int(m, zero=True):
        raise ValueError("Number of groups must be a positive integer")
    if order not in ["little", "big"]:
        raise ValueError("Bad bits group order")
    r, b = [], bin(integer)[2:]
    # pad with zeros to the left of the binary string
    b = (n - len(b) % n) % n * "0" + b
    # split the binary string into groups
    r = [b[i:i+n] for i in range(0, len(b), n)]
    # pad with groups to the left of the list of groups
    for i in range((m - len(r) % m) % m):
        r.insert(0, "0" * n)
    # then reverse per n_groups if big endian
    if order == "big":
        if m == 1:
            r = r[::-1]
        else:
            r = [i for l in [r[i:i+m][::-1] for i in range(0, len(r), m)] \
                 for i in l]
    return (sep or "").join(r)


# INTEGER <=> HEXADECIMAL STRING
def int2hex(integer, n_bytes=None):
    i, n = integer, n_bytes
    # check for input arguments
    if not is_int(i):
        raise ValueError("Bad input integer")
    if n is not None and (not is_int(n) or is_neg_int(n, zero=True)):
        raise ValueError("Number of bytes must be a positive integer")
    h = "".join("{:0>2}".join(c) for c in hex(i)[2:].rstrip("L"))
    # pad with zeros to the left of the binary string
    if n is not None:
        n *= 2
        h = (n - len(h) % n) % n * "0" + h
    return h


# INTEGER <=> 8-BITS CHARACTERS
def int2str(*integers):
    """ Convert a big integer or a list of big integers to a string of 8-bits
         characters. """
    s = ""
    for i in integers:
        _, n = "", 1
        while i > 0:
            r = i % (2 ** (8 * n))
            i -= r
            _ += chr(r // (2 ** (8 * (n - 1))))
            n += 1
        s += _[::-1]
    return s


# 8-BITS CHARACTERS <=> BINARY STRING
def str2bin(chars_string, n_bits=8, n_groups=1, sep=None, order="little"):
    """ Convert a string of 8-bits characters to a binary string (eventually
         using a separator), using a given number of bits and in little or big
         endian. """
    return int2bin(str2int(chars_string), n_bits, n_groups, sep, order)


# 8-BITS CHARACTERS <=> HEXADECIMAL STRING
def str2hex(chars_string):
    """ Convert a string of 8-bits characters to a hexadecimal string. """
    return int2hex(str2int(chars_string), len(chars_string))


# 8-BITS CHARACTERS <=> INTEGER
def str2int(chars_string, n_chars=None):
    """ Convert a string of 8-bits characters to a big integer or, if using
         blocks of n_chars characters, a list of big integers. """
    r, s, n = [], chars_string, n_chars
    # check for input arguments
    if not is_str(s):
        raise ValueError("Bad input string of 8-bits characaters")
    if n is not None and (not is_int(n) or is_neg_int(n, zero=True)):
        raise ValueError("Number of characters per block must be a positive "
                         "integer")
    if n is None:
        n = len(s)
    for i in range(0, len(s), n):
        _, chars_group = 0, s[i:i+n]
        for j, c in enumerate(chars_group[::-1]):
            _ += ord(c) * (2 ** (8 * j))
        r.append(_)
    return r[0] if len(r) == 1 else r
