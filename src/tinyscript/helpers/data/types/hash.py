# -*- coding: UTF-8 -*-
"""Hash-related checking functions and argument types.

"""
from ....preimports import re


__all__ = __features__ = []


# hash check functions
__all__ += ["is_hash", "is_md5", "is_sha1", "is_sha224", "is_sha256",
            "is_sha384", "is_sha512"]
is_hash   = lambda h: any(__check_hash(h, a, False) is not None for a in \
                          HASH_LEN.keys())
is_md5    = lambda h: __check_hash(h, "md5", False) is not None
is_sha1   = lambda h: __check_hash(h, "sha1", False) is not None
is_sha224 = lambda h: __check_hash(h, "sha224", False) is not None
is_sha256 = lambda h: __check_hash(h, "sha256", False) is not None
is_sha384 = lambda h: __check_hash(h, "sha384", False) is not None
is_sha512 = lambda h: __check_hash(h, "sha512", False) is not None


# hash-related argument types
__all__ += ["any_hash", "md5_hash", "sha1_hash", "sha224_hash", "sha256_hash",
            "sha512_hash"]
HASH_LEN = {'md5': 32, 'sha1': 40, 'sha224': 56, 'sha256': 64, 'sha384': 96,
            'sha512': 128}


def __check_hash(s, algo, fail=True):
    l = HASH_LEN[algo]
    if re.match(r"(?i)^[a-f0-9]{%d}$" % l, s) is None:
        if fail:
            raise ValueError("Bad {} hash".format(algo))
        return
    return s
md5_hash    = lambda h: __check_hash(h, "md5")
sha1_hash   = lambda h: __check_hash(h, "sha1")
sha224_hash = lambda h: __check_hash(h, "sha224")
sha256_hash = lambda h: __check_hash(h, "sha256")
sha384_hash = lambda h: __check_hash(h, "sha384")
sha512_hash = lambda h: __check_hash(h, "sha512")
md5_hash.__name__    = "MD5 hash"
sha1_hash.__name__   = "SHA1 hash"
sha224_hash.__name__ = "SHA224 hash"
sha256_hash.__name__ = "SHA256 hash"
sha384_hash.__name__ = "SHA384 hash"
sha512_hash.__name__ = "SHA512 hash"


def any_hash(h):
    if not any(__check_hash(h, a, False) is not None for a in HASH_LEN.keys()):
        raise ValueError("Bad hash")
    return h
any_hash.__name__ = "arbitrary hash"

