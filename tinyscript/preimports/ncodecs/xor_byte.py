# -*- coding: UTF-8 -*-
from ._utils import *


def _xorn(text, n=1):
    return "".join(chr(ord(c) ^ (n % 256)) for c in text)


def xor_byte_encode(i):
    def encode(text, errors="strict"):
        r = _xorn(ensure_str(text), int(i))
        return r, len(r)
    return encode
xor_byte_decode = xor_byte_encode


# note: the integer behind "xor" is captured for sending to the parametrizable
#        encode and decode functions "xor_byte_**code"
codecs.add_codec("xorN", xor_byte_encode, xor_byte_decode,
             r"(?i)xor[-_]?([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$")
