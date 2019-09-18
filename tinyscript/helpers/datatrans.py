#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common help utility help functions.

"""
import re
from six import string_types

from .types import is_bin, is_hex, is_int, is_pos_int, is_str
from ..__info__ import __author__, __copyright__, __version__


__all__ = __features__ = []


__all__ = __features__ = [
    "bin2int", "bin2hex", "bin2str",
    "hex2bin", "hex2int", "hex2str",
    "int2bin", "int2hex", "int2str",
    "str2bin", "str2int", "str2hex"
]


def __validation(**kwargs):
    """ Private generic validation function for the whole data formats. """
    for k, v in kwargs.items():
        if k == "b":
            if not is_bin(v):
                raise ValueError("Bad input binary string")
        elif k == "h":
            if not is_hex(v):
                raise ValueError("Bad input hexadecimal string")
        elif k == "i":
            if not is_int(v):
                raise ValueError("Bad input integer")
        elif k == "s":
            if not is_str(v):
                raise ValueError("Bad input string of 8-bits characaters")
        elif k in ["n_b", "n_B", "n_c", "n_g"]:
            if k in ["n_B", "n_c"] and v is None:
                continue
            if not is_pos_int(v, zero=False):
                raise ValueError("Number of {} must be a positive integer"
                                 .format({"n_b": "bits", "n_B": "bytes",
                                      "n_c": "characters", "n_g": "groups"}[k]))
        elif k == "o":
            if v not in ["little", "big"]:
                raise ValueError("Bad bits group order")


# BINARY STRING <=> HEXADECIMAL STRING
def bin2hex(binary_string, n_bits=8, n_groups=1, order="little"):
    """ Convert a binary string (eventually using a separator) to a hexadecimal
         string, using a given number of bits and in little or big endian. """
    return int2hex(bin2int(binary_string, n_bits, n_groups, order))


# BINARY STRING <=> INTEGER
def bin2int(binary_string, n_bits=8, n_groups=1, order="little"):
    """ Convert a binary string (eventually using a separator) to an integer,
         using a given number of bits and in little or big endian. """
    b, n, m = binary_string, n_bits, n_groups
    __validation(b=b, n_b=n, n_g=m, o=order)
    bits_groups = re.split(r"\W+", b)
    if len(bits_groups) == 1:
        b = bits_groups[0]
        # pad with zeros to the left of the binary string
        b = (n - len(b) % n) % n * "0" + b
        # split the binary string into groups
        bits_groups = [b[i:i+n] for i in range(0, len(b), n)]
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
def bin2str(binary_string, n_bits=8, n_groups=1, order="little"):
    """ Convert a binary string (eventually using a separator) to string of
         8-bits characters, using a given number of bits and in little or big
         endian. """
    return int2str(bin2int(binary_string, n_bits, n_groups, order))


def hex2bin(hex_string, n_bits=8, n_groups=1, sep=None, order="little"):
    """ Convert a hexadecimal string to a binary string, using a given number of
         bits and in little or big endian. """
    return int2bin(hex2int(hex_string), n_bits, n_groups, sep, order)


# HEXADECIMAL STRING <=> INTEGER
def hex2int(hex_string):
    """ Convert a hexadecimal string to a big integer. """
    h = hex_string
    __validation(h=hex_string)
    return int(h, 16)


# HEXADECIMAL STRING <=> 8-BITS CHARACTERS
def hex2str(hex_string):
    """ Convert a hexadecimal string to a string of 8-bits characters. """
    return int2str(hex2int(hex_string))


# INTEGER <=> BINARY STRING
def int2bin(integer, n_bits=8, n_groups=1, sep=None, order="little"):
    """ Convert an integer to a binary string (eventually using a separator),
         using a given number of bits and in little or big endian. """
    #FIXME: use format(int, "0Nb") with N the number of heading zeros
    n, m = n_bits, n_groups
    __validation(i=integer, n_b=n, n_g=m, o=order)
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
        r = [i for l in [r[i:i+m][::-1] for i in range(0, len(r), m)] \
             for i in l]
    return (sep or "").join(r)


# INTEGER <=> HEXADECIMAL STRING
def int2hex(integer, n_bytes=None):
    """ Convert an integer to a hexadecimal string. """
    #FIXME: use format(int, "0Nx") with N the number of hex digits to be output
    i, n = integer, n_bytes
    __validation(i=i, n_B=n)
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
        __validation(i=i)
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
    __validation(s=s, n_c=n)
    if n is None:
        n = len(s)
    for i in range(0, len(s), n):
        _, chars_group = 0, s[i:i+n]
        for j, c in enumerate(chars_group[::-1]):
            _ += ord(c) * (2 ** (8 * j))
        r.append(_)
    return r[0] if len(r) == 1 else r
