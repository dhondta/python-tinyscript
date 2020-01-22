# -*- coding: UTF-8 -*-
"""Common utility functions.

"""
import binascii
from math import ceil

from .types import is_bin, is_hex, is_int, is_pos_int, is_str
from .utils import BitArray as Bits
from ..compat import b, ensure_str


__all__ = __features__ = [
    "bin2bin", "bin2int", "bin2hex", "bin2str", "hex2bin", "hex2int", "hex2str",
    "int2bin", "int2hex", "int2str", "int2uni", "str2bin", "str2int", "str2hex",
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
                                 .format({"n_b": "bits", "n_B": "bits",
                                      "n_c": "characters", "n_g": "groups"}[k]))
        elif k == "o":
            if v not in ["little", "big"]:
                raise ValueError("Bad bits group order")


# BINARY STRING <=> *
def bin2bin(binary_string, nbits_in=8, nbits_out=8):
    """ Convert a binary string with groups of nbits_in bits to a binary string
         with groups of nbits_out bits. """
    bs = binary_string
    __validation(b=bs, n_b=nbits_in, n_B=nbits_out)
    bs = Bits(bs, nbits=nbits_in)
    bs.nbits = nbits_out
    return bs.bin


def bin2hex(binary_string, nbits_in=8, nbits_out=8):
    """ Convert a binary string (eventually using a separator) to a hexadecimal
         string, using a given number of bits and in little or big endian. """
    return Bits(bin2bin(binary_string, nbits_in, nbits_out)).hex


def bin2int(binary_string, nbits_in=8, nbits_out=8, order="big"):
    """ Convert a binary string (eventually using a separator) to an integer,
         using a given number of bits and in little or big endian. """
    __validation(o=order)
    bs = Bits(bin2bin(binary_string, nbits_in, nbits_out))
    return bs.intle if order == "little" else bs.intbe


def bin2str(binary_string, nbits_in=8, nbits_out=8):
    """ Convert a binary string to string of 8-bits characters, using a given
         number of bits. """
    bs = binary_string
    __validation(b=bs, n_b=nbits_in, n_B=nbits_out)
    bs = Bits(bs, nbits=nbits_in)
    bs.nbits = nbits_out
    return ensure_str(bs.bytes)


# HEXADECIMAL STRING <=> *
def hex2bin(hex_string, nbits_in=8, nbits_out=8):
    """ Convert a hexadecimal string to a binary string. """
    h = hex_string
    __validation(h=h, n_b=nbits_in, n_B=nbits_out)
    bs = Bits()
    bs.hex = h
    bs._nbits = nbits_in
    bs.nbits = nbits_out
    return bs.bin


def hex2int(hex_string, order="big"):
    """ Convert a hexadecimal string to a big integer. """
    h = hex_string
    __validation(h=h, o=order)
    bs = Bits()
    bs.hex = h
    return bs.intle if order == "little" else bs.intbe


def hex2str(hex_string):
    """ Convert a hexadecimal string to a string of 8-bits characters. """
    h = hex_string
    __validation(h=h)
    return ensure_str(binascii.unhexlify(b(hex_string)))


# INTEGER <=> *
def int2bin(integer, nbits_in=8, nbits_out=8, order="big"):
    """ Convert an integer to a binary string in little or big endian. """
    i = integer
    __validation(i=i, n_b=nbits_in, n_B=nbits_out, o=order)
    bs = Bits()
    bs.hex = int(ceil(max(i.bit_length(), 1) / 8.0)) * 2 * "0"
    setattr(bs, "intle" if order == "little" else "intbe", i)
    bs._nbits = nbits_in
    bs.nbits = nbits_out
    return bs.bin


def int2hex(integer, order="big"):
    """ Convert an integer to a hexadecimal string. """
    i = integer
    __validation(i=i, o=order)
    bs = Bits()
    bs.hex = int(ceil(max(i.bit_length(), 1) / 8.0)) * 2 * "0"
    setattr(bs, "intle" if order == "little" else "intbe", i)
    return bs.hex


def int2str(*integers, **kwargs):
    """ Convert a big integer or a list of big integers to a string of 8-bits
         characters. """
    order = kwargs.get('order', "big")
    s = ""
    for i in integers:
        __validation(i=i, o=order)
        bs = Bits()
        bs.hex = int(ceil(max(i.bit_length(), 1) / 8.0)) * 2 * "0"
        setattr(bs, "intle" if order == "little" else "intbe", i)
        s += ensure_str(bs.bytes)
    return s


def int2uni(*integers):
    """ Convert a big integer or a list of big integers to a unicode string. """
    s = ""
    for i in integers:
        __validation(i=i)
        s += b("\\u{:0>4}".format(hex(i)[2:])).decode('unicode-escape')
    return s


# 8-BITS CHARACTERS <=> *
def str2bin(chars_string, nbits_in=8, nbits_out=8):
    """ Convert a string of 8-bits characters to a binary string. """
    s = chars_string
    __validation(s=s, n_b=nbits_in, n_B=nbits_out)
    bs = Bits(nbits=nbits_in)
    bs.bytes = b(chars_string)
    bs.nbits = nbits_out
    return bs.bin


def str2hex(chars_string):
    """ Convert a string of 8-bits characters to a hexadecimal string. """
    s = chars_string
    __validation(s=s)
    return ensure_str(binascii.hexlify(b(s)))


def str2int(chars_string, nchars=None, order="big"):
    """ Convert a string of 8-bits characters to a big integer or, if using
         blocks of nchars characters, a list of big integers. """
    r, s, n = [], chars_string, nchars
    __validation(s=s, n_c=n, o=order)
    n = nchars or len(chars_string)
    for k in range(0, len(s), n):
        i, grp = 0, s[k:k+n]
        for j, c in enumerate(grp if order == "little" else grp[::-1]):
            i += ord(c) * (2 ** (8 * j))
        r.append(i)
    return r[0] if len(r) == 1 else r
