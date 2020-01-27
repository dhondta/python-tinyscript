# -*- coding: UTF-8 -*-
"""DNA Codec - dna content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ._utils import *


ENCMAP = {'00': "A", '10': "G", '01': "C", '11': "T"}
DECMAP = {v: k for k, v in ENCMAP.items()}
REPLACE_CHAR = "?"


class DNAError(ValueError):
    pass


class DNADecodeError(DNAError):
    pass


def dna_encode(text, errors="strict"):
    r = ""
    for c in text:
        bs = "{:0>8}".format(bin(ord(c))[2:])
        for i in range(0, 8, 2):
            r += ENCMAP[bs[i:i+2]]
    return r, len(text)


def dna_decode(text, errors="strict"):
    r = ""
    text = text.upper()
    for i in range(0, len(text), 4):
        bs = ""
        for j, c in enumerate(text[i:i+4]):
            try:
                bs += DECMAP[c]
            except KeyError:
                if errors == "strict":
                    raise DNADecodeError("'dna' codec can't decode character "
                                         "'{}' in position {}".format(c, i + j))
                elif errors == "replace":
                    bs += 2 * REPLACE_CHAR
                elif errors == "ignore":
                    continue
                else:
                    raise ValueError("Unsupported error handling {}"
                                     .format(errors))
        try:
            r += chr(int(bs, 2))
        except ValueError:
            if len(bs) > 0:
                r += "[" + bs + "]"
    return r, len(text)


codecs.add_codec("dna", dna_encode, dna_decode)
