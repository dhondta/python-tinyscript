# -*- coding: UTF-8 -*-
"""Module for enhancing hashlib preimport.

"""
import hashlib
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
            b = f.read(h.block_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()
hashlib.hash_file = hash_file


# this binds new file hashing functions to the hashlib for each existing hash
#  algorithm
for algo in [x for x in hashlib.__dict__.keys()]:
    try:
        h = hashlib.new(algo)  # this fails if the algo is not valid, then
        h.update(b(""))        #  excluding module objects that aren't hash
                               #  algorithm functions
        def _hash_file(a):
            def _wrapper(f):
                return hash_file(f, a)
            return _wrapper
        setattr(hashlib, "{}_file".format(algo), _hash_file(algo))
    except ValueError:  # triggered by h.update(b(""))
        pass
