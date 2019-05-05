#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common code-related functions.

"""
import inspect
import patchy


__all__ = __features__ = ["code_patch", "code_unpatch", "CodePatch",
                          "code_replace", "code_restore"]


code_patch   = patchy.patch
code_unpatch = patchy.unpatch
CodePatch    = patchy.temp_patch


__modified_code = {}


def code_replace(func, *replacements):
    """ Slight modification to original replace command to allow replacing only
         part(s) of code and not necessarily using whole function's code. """
    try:
        patchy.replace(func, *replacements)
        old_code = replacements[0]
    # if normal handling fails, get whole function's code first, apply
    #  replacement then retry
    except:
        if len(replacements) % 2 != 0:
            raise ValueError("Bad code replacements")
        old_code = inspect.getsource(func)
        for i in range(0, len(replacements), 2):
            new_code = old_code.replace(replacements[i], replacements[i+1])
        patchy.replace(func, old_code, new_code)
    __modified_code[func] = old_code


def code_restore(func):
    """ Additional function to restore mofidied code. """
    old_code = __modified_code.get(func)
    if old_code is not None:
        old_code = patchy.api.dedent(old_code)
        patchy.api._set_source(func, old_code)


# disable source AST check in _assert_ast_equal to avoid Python compatibility
#  errors
code_replace(patchy.api._assert_ast_equal,
             "current_ast = ast.parse",
             "return #current_ast = ast.parse")
