#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Deprecation warnings, for use when no backward-compatibility provided.

"""


from .__info__ import __author__, __copyright__, __version__


__all__ = __features__ = []


def __deprecated(old, new=None):
    raise DeprecationWarning("'{}' has been deprecated{}".format(old,
                            [", please use '{}'".format(new), ""][new is None]))


__all__ += ["bin2txt", "is_lst", "txt2bin"]
bin2txt = lambda *a, **kw: __deprecated("bin2txt", "bin2str")
is_lst  = lambda *a, **kw: __deprecated("is_lst", "is_list")
txt2bin = lambda *a, **kw: __deprecated("txt2bin", "str2bin")
