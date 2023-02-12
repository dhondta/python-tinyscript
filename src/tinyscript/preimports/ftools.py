# -*- coding: UTF-8 -*-
"""Module for enhancing functools preimport.

Source: https://stackoverflow.com/questions/43506378/how-to-get-source-code-of-function-that-is-wrapped-by-a-decorator

"""
import functools
import sys


if sys.version_info < (3,):
    def add_wrapped_dunder(uw):
        """ This adds the __wrapped__ dunder to a wrapped function. This is implemented from Python 3.2 and is thus
             added for compatibility with Python 2. """
        @functools.wraps(uw)
        def update_wrapper(wrapper, wrapped, assigned=functools.WRAPPER_ASSIGNMENTS, updated=functools.WRAPPER_UPDATES):
            wrapper = uw(wrapper, wrapped, assigned, updated)
            wrapper.__wrapped__ = wrapped
            return wrapper
        return update_wrapper
    functools.update_wrapper = add_wrapped_dunder(functools.update_wrapper)

