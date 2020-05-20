# -*- coding: UTF-8 -*-
"""Module for enhancing hashlib preimport.

"""
import hashlib
from os.path import expanduser, isfile
from six import b


def hash_file(filename, algo="sha256"):
    """
    This extends hashlib's hashing function to hash a file per block.

    :param filename: name of the file to be hashed
    :return:         ALGO(file)
    """
    h = hashlib.new(algo)
    with open(filename, 'rb') as f:
        while True:
            data = f.read(h.block_size)
            if not data:
                break
            h.update(data)
    return h.hexdigest()
hashlib.hash_file = hash_file


# this binds new file hashing functions to the hashlib for each existing hash algorithm
for algo in [x for x in hashlib.__dict__.keys()]:
    try:
        h = hashlib.new(algo)
        h.update(b(""))
        def _hash_file(a):
            def _wrapper(f):
                return hash_file(f, a)
            return _wrapper
        setattr(hashlib, "{}_file".format(algo), _hash_file(algo))
    except ValueError:  # unsupported hash type
        pass


class LookupTable(dict):
    """
    Lookup table class for password cracking.

    :param dict_path:   path of the dictionary file to be loaded
    :param algorithm:   the hash algorithm to be used
    :param ratio:       ratio of value to be hashed in the lookup table (by default, every value is considered but, i.e.
                         with a big wordlist, a ratio of 2/3/4/5/... can be used in order to limit the memory load)
    :param dict_filter: function aimed to filter the words from the dictionary (e.g. only alpha-numeric)
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

