# -*- coding: UTF-8 -*-
try:                 # Python 2
    from string import maketrans
except ImportError:  # Python 3
    maketrans = str.maketrans

from ._utils import *


alph      = "abeiostABEIOSTZ", "483105748310572"
to_leet   = maketrans(*alph)
from_leet = maketrans(*alph[::-1])


def leet_encode(text, errors="strict"):
    r = text.translate(to_leet)
    return r, len(r)

def leet_decode(text, errors="strict"):
    r = text.translate(from_leet)
    return r, len(r)


# note: the integer behind "rot" is captured for sending to the parametrizable
#        encode and decode functions "_rotn_**code"
codecs.add_codec("leet", leet_encode, leet_decode,
                 r"(?:leet|1337|leetspeak|13375p34k)$")
