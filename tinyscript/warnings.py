#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Deprecation warnings, for use when no backward-compatibility provided.

"""
__all__ = __features__ = []


def __deprecated(old, new=None):
    msg = "'{}' has been deprecated".format(old)
    if new is not None:
        msg += ", please use '{}'".format(new)
    raise DeprecationWarning(msg)


# Jan 2020: removal of helpers.patch and new preimports.code
__codefuncs__ = [
    "code_patch", "code_unpatch", "code_add_block", "code_source",
    "code_add_line", "code_add_lines", "code_delete_line", "code_delete_lines",
    "code_insert_block", "code_insert_line", "code_insert_lines",
    "code_remove_line", "code_remove_lines", "code_replace",
    "code_replace_line", "code_replace_lines", "code_restore", "code_revert",
]
__all__ += __codefuncs__ + ["CodePatch"]
for f in __codefuncs__:
    globals()[f] = eval("lambda *a, **kw: __deprecated(\"{}\", \"{}\")"
                        .format(f, f.replace("_", ".", 1)))
CodePatch = lambda *a, **kw: __deprecated("CodePatch", "code.Patch")

# Jan 2020: move of helpers under a "god" module
from tinyscript.helpers import __helpers__
__all__ += __helpers__
for f in __helpers__:
    globals()[f] = eval("lambda *a, **kw: __deprecated(\"{}\", \"{}\")"
                        .format(f, "ts." + f))
