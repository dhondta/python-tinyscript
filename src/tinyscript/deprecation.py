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

