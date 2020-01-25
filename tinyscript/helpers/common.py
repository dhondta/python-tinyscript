# -*- coding: UTF-8 -*-
"""Common utility functions.

"""
from itertools import cycle, permutations, product
from six import string_types
from string import printable
from subprocess import Popen, PIPE

from .compat import b
from .constants import PYTHON3


__all__ = __features__ = ["bruteforce", "execute", "strings",
                          "strings_from_file", "xor"]


def xor(str1, str2, offset=0):
    """
    Function for XORing two strings of different length. Either the first of the
     second string can be longer than the other.

    :param str1:   first string, with length L1
    :param str2:   second string, with length L2
    :param offset: ASCII offset to be applied on each resulting character
    """
    r = ""
    for c1, c2 in zip(cycle(str1) if len(str1) < len(str2) else str1,
                      cycle(str2) if len(str2) < len(str1) else str2):
        r += chr(((ord(c1) ^ ord(c2)) + offset) % 256)
    return r


def bruteforce(maxlen, alphabet=tuple(map(chr, range(256))), minlen=1,
               repeat=True):
    """
    Generator for bruteforcing according to minimum and maximum lengths and an
     alphabet.
    
    :param maxlen:   maximum bruteforce entry length
    :param alphabet: bruteforce alphabet to be used
    :param minlen:   minimum bruteforce entry length (optional)  
    :yield:          bruteforce entry
    """
    for i in range(minlen, maxlen + 1):
        if repeat:
            for c in product(alphabet, repeat=i):
                yield c if isinstance(c[0], int) else ''.join(c)
        else:
            for c in permutations(alphabet, i):
                yield c if isinstance(c[0], int) else ''.join(c)


def execute(cmd, **kwargs):
    """
    Dummy wrapper for subprocess.Popen.
    
    :param cmd: command string
    """
    if isinstance(cmd, string_types):
        cmd = cmd.split()
    return Popen(cmd, stdout=PIPE, stderr=PIPE, **kwargs).communicate()


def strings(data, minlen=4, alphabet=printable):
    """
    Generator yielding strings according to a charset and a minimal length from
     a given string buffer.
    
    :param filename: input file
    :param minlen:   minimal length of strings to be considered
    :param alphabet: valid charset for the strings
    """
    result = ""
    for c in b(data):
        if c in b(alphabet):
            result += chr(c) if PYTHON3 else c
            continue
        if len(result) >= minlen:
            yield result
        result = ""
    if len(result) >= minlen:
        yield result


def strings_from_file(filename, minlen=4, alphabet=printable, offset=0):
    """
    Generator yielding strings according to a charset and a minimal length from
     a given file.
    
    :param filename: input file
    :param minlen:   minimal length of strings to be considered
    :param alphabet: valid charset for the strings
    :param offset:   start offset in the input file
    """
    with open(filename, 'rb') as f:
        f.seek(offset)
        result = ""
        while True:
            data = f.read(1024)
            if not data:
                break
            for c in data:
                if c in b(alphabet):
                    result += chr(c) if PYTHON3 else c
                    continue
                if len(result) >= minlen:
                    yield result
                result = ""
        if len(result) >= minlen:
            yield result
