# -*- coding: UTF-8 -*-
"""Common data transformation functions.

"""
from ..types import is_bin, is_bytes, is_hex, is_int, is_list, is_pos_int, is_str
from ..utils import BitArray as Bits
from ...common import lazy_load_module
from ...compat import b, ensure_str

for _m in ["binascii", "functools", "math"]:
    lazy_load_module(_m)


__all__ = __features__ = [
    "bin2bin", "bin2int", "bin2hex", "bin2str", "hex2bin", "hex2int", "hex2str",
    "int2bin", "int2hex", "int2str", "int2uni", "lst2str", "str2bin", "str2int", "str2hex", "str2lst",
]


padz = lambda s, n: s.zfill(len(s) + (n - len(s) % n) % n)


def __validation(**kwargs) -> None:
    """ Private generic validation function for the whole data formats. """
    for k, v in kwargs.items():
        if k == "b":
            if not is_bin(v):
                raise ValueError(f"Bad input binary string '{v}'")
        elif k == "h":
            if not is_hex(v):
                raise ValueError(f"Bad input hexadecimal string '{v}'")
        elif k == "i":
            if not is_int(v):
                raise ValueError(f"Bad input integer {v}")
        elif k == "l":
            if not is_list(v):
                raise ValueError(f"Bad input list {v}")
        elif k in ["n_b", "n_B", "n_c", "n_g"]:
            if not is_pos_int(v, zero=False):
                raise ValueError("Number of {} must be a positive int, not {}"
                                 .format({"n_b": "bits", "n_B": "bits", "n_c": "characters", "n_g": "groups"}[k], v))
        elif k == "o":
            if v not in ["little", "big"]:
                raise ValueError(f"Bad bits group order '{v}'")
        elif k == "s":
            if not is_str(v):
                raise ValueError(f"Bad input string of 8-bits characaters '{v}'")
        elif k == "u":
            if not isinstance(v, bool):
                raise ValueError(f"Bad value for input boolean {v}")
        else:
            if v is None:
                continue
            if not is_pos_int(v, zero=False):
                raise ValueError(f"{k} must be a positive int, not {v}")


# BINARY STRING ==> *
def __ensure_bitstring(f):
    """ Ensure that an input valid binary data is converted to a bitstring. A valid binary data can be a bitstring, a
         list of integer ones/zeros or a list of string ones/zeros. """
    @functools.wraps(f)
    def _wrapper(binary, *a, **kw) -> str:
        if is_list(binary):
            binary = lst2str(binary, "")
        return f(binary, *a, **kw)
    return _wrapper


# BINARY STRING ==> *
@__ensure_bitstring
def bin2bin(binary_string, nbits_in=8, nbits_out=8) -> str:
    """ Convert a binary string with groups of nbits_in bits to a binary string with groups of nbits_out bits. """
    bs, n_b, n_B = binary_string, nbits_in, nbits_out
    __validation(b=bs, n_b=n_b, n_B=n_B)
    if len(bs) < n_B:
        return bs.zfill(n_B)
    if n_b == n_B:
        return padz(bs, n_b)
    return "".join(bs[i:i+n_b][max(0, n_b-n_B):].zfill(n_B) for i in range(0, len(bs), n_b) if i+n_b <= len(bs))


@__ensure_bitstring
def bin2hex(binary_string, nbits_in=8, nbits_out=8) -> str:
    """ Convert a binary string (eventually using a separator) to a hexadecimal string, using a given number of bits and
         in little or big endian. """
    h = str(hex(int(bin2bin(binary_string, nbits_in, nbits_out), 2)))[2:]
    return h.zfill(len(h) + len(h) % 2)


@__ensure_bitstring
def bin2int(binary_string, nbits_in=8, nbits_out=8, order="big", unsigned=True) -> int:
    """ Convert a binary string (eventually using a separator) to an integer, using a given number of bits and in little
         or big endian. """
    bs = binary_string
    __validation(b=bs, o=order, u=unsigned)
    bs, pref = Bits(bin2bin(bs, nbits_in, nbits_out)), ["", "u"][unsigned]
    return getattr(bs, pref + ("intle" if order == "little" else "intbe"))


@__ensure_bitstring
def bin2str(binary_string, nbits_in=8, nbits_out=8) -> str:
    """ Convert a binary string to string of 8-bits characters, using a given number of bits. """
    bs, n_b, n_B = binary_string, nbits_in, nbits_out
    __validation(b=bs, n_b=nbits_in, n_B=nbits_out)
    bs = bin2bin(bs, n_b, n_B)
    if n_B != 8:
        bs = bin2bin(bs, n_B, 8)
    return "".join(chr(int(bs[i:i+8], 2)) for i in range(0, len(bs), 8))


# HEXADECIMAL STRING ==> *
def hex2bin(hex_string, nbits_in=8, nbits_out=8) -> str:
    """ Convert a hexadecimal string to a binary string. """
    h, n_b, n_B = hex_string, nbits_in, nbits_out
    __validation(h=h, n_b=n_b, n_B=n_B)
    bs = bin(int(h, 16))[2:]
    return bin2bin(padz(bs, n_b), n_b, n_B)


def hex2int(hex_string, order="big", unsigned=True) -> int:
    """ Convert a hexadecimal string to a big integer. """
    h = hex_string
    __validation(h=h, o=order, u=unsigned)
    bs = Bits()
    bs.hex = h
    pref = ["", "u"][unsigned]
    return getattr(bs, pref + ("intle" if order == "little" else "intbe"))


def hex2str(hex_string) -> str:
    """ Convert a hexadecimal string to a string of 8-bits characters. """
    h = hex_string
    __validation(h=h)
    return ensure_str(binascii.unhexlify(b(hex_string)))


# INTEGER ==> *
def int2bin(integer, nbits_in=8, nbits_out=8, order="big", unsigned=True) -> str:
    """ Convert an integer to a binary string in little or big endian. """
    i = integer
    __validation(i=i, n_b=nbits_in, n_B=nbits_out, o=order, u=unsigned)
    bs = Bits()
    nbits = i.bit_length() + int(not unsigned)
    bs.hex = int(math.ceil(max(nbits, 1) / 8.0)) * 2 * "0"
    pref = ["", "u"][unsigned]
    setattr(bs, pref + ("intle" if order == "little" else "intbe"), i)
    bs._nbits = nbits_in
    bs.nbits = nbits_out
    return bs.bin


def int2hex(integer, order="big", unsigned=True) -> str:
    """ Convert an integer to a hexadecimal string. """
    i = integer
    __validation(i=i, o=order, u=unsigned)
    bs = Bits()
    nbits = i.bit_length() + int(not unsigned)
    bs.hex = int(math.ceil(max(nbits, 1) / 8.0)) * 2 * "0"
    pref = ["", "u"][unsigned]
    setattr(bs, pref + ("intle" if order == "little" else "intbe"), i)
    return bs.hex
    #"".join([h[i:i+2] for i in range(0, len(h), 2)][::-1])


def int2str(integer, order="big", unsigned=True) -> str:
    """ Convert a big integer to a string of 8-bits characters. """
    i = integer
    __validation(i=i, o=order, u=unsigned)
    bs = Bits()
    nbits = i.bit_length() + int(not unsigned)
    bs.hex = int(math.ceil(max(nbits, 1) / 8.0)) * 2 * "0"
    pref = ["", "u"][unsigned]
    setattr(bs, pref + ("intle" if order == "little" else "intbe"), i)
    return ensure_str(bs.bytes)


def int2uni(integer) -> str:
    """ Convert an integer to a unicode string. """
    i = integer
    __validation(i=i)
    return b("\\u{:0>4}".format(hex(i)[2:])).decode('unicode-escape')


def lst2str(lst, sep=",") -> str:
    """ Convert a list of items to a string. """
    __validation(l=lst)
    return sep.join(map(str, lst))


# 8-BITS CHARACTERS ==> *
def str2bin(chars_string, nbits_in=8, nbits_out=8) -> str:
    """ Convert a string of 8-bits characters to a binary string. """
    s, n_b, n_B = chars_string, nbits_in, nbits_out
    __validation(s=s, n_b=n_b, n_B=n_B)
    return bin2bin("".join(format(i, 'b').zfill(n_b) for i in bytearray(s, 'utf-8')), n_b, n_B)


def str2hex(chars_string) -> str:
    """ Convert a string of 8-bits characters to a hexadecimal string. """
    s = chars_string
    __validation(s=s)
    return ensure_str(binascii.hexlify(b(s)))


def str2int(chars_string, order="big", unsigned=True) -> int:
    """ Convert a string of 8-bits characters to a big integer or, if using blocks of nchars characters, a list of big
         integers. """
    s = chars_string
    __validation(s=s, o=order, u=unsigned)
    bs = Bits()
    bs.bytes = b(s)
    pref = ["", "u"][unsigned]
    return getattr(bs, pref + ("intle" if order == "little" else "intbe"))


def str2lst(chars_string) -> list:
    """ Convert a string of 8-bits characters to a list of items, converted into integers if relevant. """
    s = chars_string
    __validation(s=s)
    return [int(c) if is_str(c) and c.isdigit() else c for c in s]


# add multi-input conversion functions
def __items2something(f):
    """ Decorate [in-fmt]2[out-fmt] functions to make [in-fmt]s2[out-fmt] (taking multiple inputs, producing a single
         output (i.e. ints2hex, strs2int, ...). """
    infmt, outfmt = f.__name__.split("2")
    @functools.wraps(f)
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
    @functools.wraps(f)
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
                    inl = int(math.ceil(len(data) / float(n)))
                for i in range(0, len(data), inl):
                    r.append(func(data[i:i+inl], **kwargs))
            else:
                out = func(data, **kwargs)
                if n is not None:
                    outl = int(math.ceil(len(out) / float(n)))
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

