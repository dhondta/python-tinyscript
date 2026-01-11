# -*- coding: UTF-8 -*-
"""Module for enhancing hashlib preimport.

"""
import hashlib
from os.path import expanduser, isfile

from ..helpers.compat import b


def hash_file(filename, algo="sha256"):
    """ This extends hashlib's hashing function to hash a file per block.

    :param filename: name of the file to be hashed
    :return:         ALGO(file)
    """
    try:
        h = hashlib.new(algo)
    except ValueError:  # unsupported hash type
        try:
            h = hashlib.__dict__[algo]()
        except KeyError:
            raise ValueError(f"unsupported hash type {algo}")
    with open(filename, 'rb') as f:
        while True:
            data = f.read(h.block_size)
            if not data:
                break
            h.update(data)
    return h.hexdigest()
hashlib.hash_file = hash_file


def mmh3_32(data: bytes = b"", seed: int = 0):
    """ 32-bit MurmurHash3 """
    from mmh3 import mmh3_32 as _mmh3_32
    class mmh3_32:
        __module__ = "builtins"
        _h: _mmh3_32
        def __init__(self, data: bytes = b"", seed: int = 0) -> None: self._h = _mmh3_32(data, seed)
        def copy(self) -> "mmh3_32":
            cls = self.__class__.__new__(self.__class__)
            cls._h = self._h.copy()
            return cls
        def digest(self) -> bytes: return self._h.digest()
        def hexdigest(self) -> str: return self._h.digest().hex()
        def sintdigest(self) -> int: return self._h.sintdigest()
        def uintdigest(self) -> int: return self._h.uintdigest()
        def update(self, data: bytes) -> None: self._h.update(data)
        block_size = property(lambda self: self._h.block_size)
        digest_size = property(lambda self: self._h.digest_size)
        name = property(lambda self: self._h.name)
    return mmh3_32(data, seed)
hashlib.mmh3_32 = mmh3_32
hashlib.algorithms_available.add("mmh3_32")


def mmh3_128(data: bytes = b"", seed: int = 0):
    """ 128-bit MurmurHash3 """
    from mmh3 import mmh3_x64_128 as _mmh3_x64_128
    class mmh3_128:
        __module__ = "builtins"
        _h: _mmh3_x64_128
        def __init__(self, data: bytes = b"", seed: int = 0) -> None: self._h = _mmh3_x64_128(data, seed)
        def copy(self) -> "mmh3_128":
            cls = self.__class__.__new__(self.__class__)
            cls._h = self._h.copy()
            return cls
        def digest(self) -> bytes: return self._h.digest()
        def hexdigest(self) -> str: return self._h.digest().hex()
        def sintdigest(self) -> int: return self._h.sintdigest()
        def uintdigest(self) -> int: return self._h.uintdigest()
        def update(self, data: bytes) -> None: self._h.update(data)
        block_size = property(lambda self: self._h.block_size)
        digest_size = property(lambda self: self._h.digest_size)
        name = property(lambda self: self._h.name)
    return mmh3_128(data, seed)
hashlib.mmh3_128 = mmh3_128
hashlib.algorithms_available.add("mmh3_128")


# this binds new file hashing functions to the hashlib for each existing hash algorithm
for algo in hashlib.algorithms_available:
    try:
        h = hashlib.new(algo)
    except ValueError:  # unsupported hash type
        h = hashlib.__dict__[algo]()
    h.update(b"")
    def _hash_file(a):
        def _wrapper(f):
            return hash_file(f, a)
        return _wrapper
    setattr(hashlib, f"{algo}_file", _hash_file(algo))


class LookupTable(dict):
    """ Lookup table class for password cracking.

    :param dict_path:   path of the dictionary file to be loaded
    :param algorithm:   the hash algorithm to be used
    :param ratio:       ratio of value to be hashed in the lookup table (by default, every value is considered but, i.e.
                         with a big wordlist, a ratio of 2/3/4/5/... can be used in order to limit the memory load)
    :param dict_filter: function aimed to filter the words from the dictionary (e.g. only alphanumeric)
    :param prefix:      prefix to be prepended to passwords (e.g. a salt)
    :param suffix:      suffix to be appended to passwords (e.g. a salt)
    """
    def __init__(self, dict_path, algorithm="md5", ratio=1., dict_filter=None, prefix=None, suffix=None):
        dict_path = expanduser(dict_path)
        if not isfile(dict_path):
            raise ValueError("Bad dictionary file path")
        if algorithm not in hashlib.algorithms_available:
            raise ValueError("Bad hashing algorithm")
        if not isinstance(ratio, float) or ratio <= 0. or ratio > 1.:
            raise ValueError("Bad ratio")
        h = lambda x: getattr(hashlib, algorithm)(b(prefix or "") + b(x) + b(suffix or "")).hexdigest()
        with open(dict_path) as f:
            self.filtered = 0
            m = round(1 / float(ratio))
            for i, l in enumerate(f):
                if (i - self.filtered) % m == 0:
                    l = l.strip()
                    if dict_filter is None or hasattr(dict_filter, '__call__') and dict_filter(l):
                        self[h(l)] = l
                    else:
                        self.filtered += 1
hashlib.LookupTable = LookupTable

