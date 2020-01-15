# -*- coding: UTF-8 -*-
"""Common utility functions.

"""
from itertools import product
from six import string_types
from subprocess import Popen, PIPE


__all__ = __features__ = ["bruteforce", "execute"]


def bruteforce(maxlen, alphabet=tuple(map(chr, range(256))), minlen=1):
    """
    Generator for bruteforcing according to minimum and maximum lengths and an
     alphabet.
    
    :param maxlen:   maximum bruteforce entry length
    :param alphabet: bruteforce alphabet to be used
    :param minlen:   minimum bruteforce entry length (optional)  
    :yield:          bruteforce entry
    """
    for i in range(minlen, maxlen + 1):
        for c in product(alphabet, repeat=i):
            yield c if isinstance(c[0], int) else ''.join(c)


def execute(cmd, **kwargs):
    """
    Dummy wrapper for subprocess.Popen.
    
    :param cmd: command string
    """
    if isinstance(cmd, string_types):
        cmd = cmd.split()
    return Popen(cmd, stdout=PIPE, stderr=PIPE, **kwargs).communicate()
