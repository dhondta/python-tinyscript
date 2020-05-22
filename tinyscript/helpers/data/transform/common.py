# -*- coding: UTF-8 -*-
"""Common data transformation functions.

"""
import binascii
from functools import wraps
from math import ceil

from ..types import is_bin, is_bytes, is_hex, is_int, is_list, is_pos_int, is_str
from ..utils import BitArray as Bits
from ...compat import b, ensure_str


__all__ = __features__ = [
    "bin2bin", "bin2int", "bin2hex", "bin2str",
    "hex2bin", "hex2int", "hex2str",
    "int2bin", "int2hex", "int2str", "int2uni",
    "lst2str",
    "str2bin", "str2int", "str2hex", "str2lst",
]


def __validation(**kwargs):
    """ Private generic validation function for the whole data formats. """
    for k, v in kwargs.items():
        if k == "b":
            if not is_bin(v):
                raise ValueError("Bad input binary string '{}'".format(v))
        elif k == "h":
            if not is_hex(v):
                raise ValueError("Bad input hexadecimal string '{}'".format(v))
        elif k == "i":
            if not is_int(v):
                raise ValueError("Bad input integer {}".format(v))
        elif k == "l":
            if not is_list(v):
                raise ValueError("Bad input list {}".format(v))
        elif k in ["n_b", "n_B", "n_c", "n_g"]:
            if not is_pos_int(v, zero=False):
                raise ValueError("Number of {} must be a positive int, not {}"
                                 .format({"n_b": "bits", "n_B": "bits", "n_c": "characters", "n_g": "groups"}[k], v))
        elif k == "o":
            if v not in ["little", "big"]:
                raise ValueError("Bad bits group order '{}'".format(v))
        elif k == "s":
            if not is_str(v):
                raise ValueError("Bad input string of 8-bits characaters '{}'".format(v))
        elif k == "u":
            if not isinstance(v, bool):
                raise ValueError("Bad value for input boolean {}".format(v))
        else:
            if v is None:
                continue
            if not is_pos_int(v, zero=False):
                raise ValueError("{} must be a positive int, not {}".format(k, v))


# BINARY STRING ==> *
def __ensure_bitstring(binary):
    """ Ensure that an input valid binary data is converted to a bitstring. A valid binary data can be a bitstring, a
         list of integer ones/zeros or a list of string ones/zeros. """
    if is_list(binary):
        binary = lst2str(binary, "")
    return binary


def bin2bin(binary_string, nbits_in=8, nbits_out=8):
    """ Convert a binary string with groups of nbits_in bits to a binary string with groups of nbits_out bits. """
    bs = __ensure_bitstring(binary_string)
    __validation(b=bs, n_b=nbits_in, n_B=nbits_out)
    bs = Bits(bs, nbits=nbits_in)
    bs.nbits = nbits_out
    return bs.bin


def bin2hex(binary_string, nbits_in=8, nbits_out=8):
    """ Convert a binary string (eventually using a separator) to a hexadecimal string, using a given number of bits and
         in little or big endian. """
    bs = __ensure_bitstring(binary_string)
    return Bits(bin2bin(bs, nbits_in, nbits_out)).hex


def bin2int(binary_string, nbits_in=8, nbits_out=8, order="big", unsigned=True):
    """ Convert a binary string (eventually using a separator) to an integer, using a given number of bits and in little
         or big endian. """
    bs = __ensure_bitstring(binary_string)
    __validation(b=bs, o=order, u=unsigned)
    bs = Bits(bin2bin(bs, nbits_in, nbits_out))
    pref = ["", "u"][unsigned]
    return getattr(bs, pref + ("intle" if order == "little" else "intbe"))


def bin2str(binary_string, nbits_in=8, nbits_out=8):
    """ Convert a binary string to string of 8-bits characters, using a given number of bits. """
    bs = __ensure_bitstring(binary_string)
    __validation(b=bs, n_b=nbits_in, n_B=nbits_out)
    bs = Bits(bs, nbits=nbits_in)
    bs.nbits = nbits_out
    return bs.bytes


# HEXADECIMAL STRING ==> *
def hex2bin(hex_string, nbits_in=8, nbits_out=8):
    """ Convert a hexadecimal string to a binary string. """
    h = hex_string
    __validation(h=h, n_b=nbits_in, n_B=nbits_out)
    bs = Bits()
    bs.hex = h
    bs._nbits = nbits_in
    bs.nbits = nbits_out
    return bs.bin


def hex2int(hex_string, order="big", unsigned=True):
    """ Convert a hexadecimal string to a big integer. """
    h = hex_string
    __validation(h=h, o=order, u=unsigned)
    bs = Bits()
    bs.hex = h
    pref = ["", "u"][unsigned]
    return getattr(bs, pref + ("intle" if order == "little" else "intbe"))


def hex2str(hex_string):
    """ Convert a hexadecimal string to a string of 8-bits characters. """
    h = hex_string
    __validation(h=h)
    return binascii.unhexlify(b(hex_string))


# INTEGER ==> *
def int2bin(integer, nbits_in=8, nbits_out=8, order="big", unsigned=True):
    """ Convert an integer to a binary string in little or big endian. """
    i = integer
    __validation(i=i, n_b=nbits_in, n_B=nbits_out, o=order, u=unsigned)
    bs = Bits()
    nbits = i.bit_length() + int(not unsigned)
    bs.hex = int(ceil(max(nbits, 1) / 8.0)) * 2 * "0"
    pref = ["", "u"][unsigned]
    setattr(bs, pref + ("intle" if order == "little" else "intbe"), i)
    bs._nbits = nbits_in
    bs.nbits = nbits_out
    return bs.bin


def int2hex(integer, order="big", unsigned=True):
    """ Convert an integer to a hexadecimal string. """
    i = integer
    __validation(i=i, o=order, u=unsigned)
    bs = Bits()
    nbits = i.bit_length() + int(not unsigned)
    bs.hex = int(ceil(max(nbits, 1) / 8.0)) * 2 * "0"
    pref = ["", "u"][unsigned]
    setattr(bs, pref + ("intle" if order == "little" else "intbe"), i)
    return bs.hex


def int2str(integer, order="big", unsigned=True):
    """ Convert a big integer to a string of 8-bits characters. """
    i = integer
    __validation(i=i, o=order, u=unsigned)
    bs = Bits()
    nbits = i.bit_length() + int(not unsigned)
    bs.hex = int(ceil(max(nbits, 1) / 8.0)) * 2 * "0"
    pref = ["", "u"][unsigned]
    setattr(bs, pref + ("intle" if order == "little" else "intbe"), i)
    return bs.bytes


def int2uni(integer):
    """ Convert an integer to a unicode string. """
    i = integer
    __validation(i=i)
    return b("\\u{:0>4}".format(hex(i)[2:])).decode('unicode-escape')


# LIST OF ITEMS ==> STRING
def lst2str(lst, sep=","):
    """ Convert a list of items to a string. """
    __validation(l=lst)
    return sep.join(map(str, lst))


# 8-BITS CHARACTERS ==> *
def str2bin(chars_string, nbits_in=8, nbits_out=8):
    """ Convert a string of 8-bits characters to a binary string. """
    s = chars_string
    __validation(s=s, n_b=nbits_in, n_B=nbits_out)
    bs = Bits(nbits=nbits_in)
    bs.bytes = b(s)
    bs.nbits = nbits_out
    return bs.bin


def str2hex(chars_string):
    """ Convert a string of 8-bits characters to a hexadecimal string. """
    s = chars_string
    __validation(s=s)
    return binascii.hexlify(b(s))


def str2int(chars_string, order="big", unsigned=True):
    """ Convert a string of 8-bits characters to a big integer or, if using blocks of nchars characters, a list of big
         integers. """
    s = chars_string
    __validation(s=s, o=order, u=unsigned)
    bs = Bits()
    bs.bytes = b(s)
    pref = ["", "u"][unsigned]
    return getattr(bs, pref + ("intle" if order == "little" else "intbe"))


def str2lst(chars_string):
    """ Convert a string of 8-bits characters to a list of items, converted into integers if relevant. """
    s = chars_string
    __validation(s=s)
    return [int(c) if is_str(c) and c.isdigit() else c for c in s]


# make conversion functions compatible with input/output strings/bytes
def __fix_inout_formats(f):
    @wraps(f)
    def _wrapper(*args, **kwargs):
        a0 = args[0]
        a0 = ensure_str(a0) if is_str(a0) or is_bytes(a0) else a0
        r = f(a0, *args[1:], **kwargs)
        return r if is_int(r) else b(r) if is_bytes(args[0]) else ensure_str(r)
    return _wrapper


for f in __features__:
    if f in ["int2uni", "str2lst"]:
        continue
    globals()[f] = __fix_inout_formats(globals()[f])


# add multi-input conversion functions
def __items2something(f):
    """ Decorate infmt2outfmt functions to make intfmtS2outfmt (taking multiple inputs, producing a single output. """
    infmt, outfmt = f.__name__.split("2")
    @wraps(f)
    def _wrapper(*args, **kwargs):
        r = [] if outfmt == "int" else ""
        for arg in args:
            out = f(arg, **kwargs)
            if outfmt == "int":
                r.append(out)
            else:
                r += out
        return str2int(ints2str(*r)) if outfmt == "int" else r
    _wrapper.__name__ = "{}s2{}".format(infmt, outfmt)
    _wrapper.__doc__ = f.__doc__
    return _wrapper


def __something2items(f):
    """ Decorate infmt2outfmt functions to make intfmt2outfmtS (taking a single input, producing multiple outputs. """
    infmt, outfmt = f.__name__.split("2")
    @wraps(f)
    def _wrapper(data, **kwargs):
        func = f
        n = kwargs.pop('n_chunks', None)
        inl = kwargs.pop('len_in', None)
        outl = kwargs.pop('len_out', None)
        __validation(n_chunks=n, len_in=inl, len_out=outl)
        if not n and not inl and not outl:
            n = 1
        r = []
        # if input chunk length is given, process the data per block
        if n is None and inl is not None:
            if infmt == "int":
                data = int2bin(data, **kwargs)
                func = globals()['bin2' + outfmt]
            for i in range(0, len(data), inl):
                r.append(func(data[i:i+inl], **kwargs))
        # otherwise, chunk the output
        else:
            if outfmt == "int":
                if n is not None:
                    inl = int(ceil(len(data) / float(n)))
                for i in range(0, len(data), inl):
                    r.append(func(data[i:i+inl], **kwargs))
            else:
                out = func(data, **kwargs)
                if n is not None:
                    outl = int(ceil(len(out) / float(n)))
                for i in range(0, len(out), outl):
                    r.append(out[i:i+outl])
        return r
    _wrapper.__name__ = "{}2{}s".format(infmt, outfmt)
    _wrapper.__doc__ = f.__doc__
    return _wrapper


for fname in __features__[:]:
    f1 = __items2something(globals()[fname])
    globals()[f1.__name__] = f1
    f2 = __something2items(globals()[fname])
    globals()[f2.__name__] = f2
    __features__ += [f1.__name__, f2.__name__]


# FLAGS <=> INTEGER
__features__ += ["flags2int", "int2flags"]


def flags2int(*flags):
    """ Convert a list of booleans to an integer representing binary flags. """
    return int("".join(map(lambda x: "01"[bool(x)], flags)), 2)


def int2flags(integer):
    """ Convert an integer representing binary flags to a list of booleans. """
    i = integer
    __validation(i=i)
    return list(map(lambda x: x == "1", bin(i)[2:]))

