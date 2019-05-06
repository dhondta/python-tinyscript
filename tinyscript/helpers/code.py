#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common code-related functions.

"""
import patchy
from collections import deque
from six import string_types


__all__ = __features__ = ["code_patch", "code_unpatch", "CodePatch",
                          "code_replace", "code_replace_lines",
                          "code_restore", "code_revert", "code_source"]


N_MODIF = 3


code_patch   = patchy.patch
code_unpatch = patchy.unpatch
CodePatch    = patchy.temp_patch 


__orig_code = {}
__old_code = {}


class ReplacementFormatError(ValueError):
    pass


def cache(f):
    def _wrapper(*args, **kwargs):
        cache = kwargs.pop("cache", True)
        if cache:
            func = args[0]
            old_code = code_source(func)
        f(*args)
        if cache:
            if __orig_code.get(func) is None:
                __orig_code[func] = old_code
            if __old_code.get(func) is None:
                __old_code[func] = deque([], N_MODIF)
            __old_code[func].append(old_code)
    return _wrapper


@cache
def code_replace(func, *replacements):
    """
    Slight modification to original replace function to allow replacing only
     part(s) of code and not necessarily using whole function's code.
    
    :param func:         function object to be modified
    :param replacements: list of replacements - pairs (str_to_repl, replac)
    """
    try:
        patchy.replace(func, *replacements)
    # if normal handling fails, get whole function's code first, apply
    #  replacement then retry
    except:
        if len(replacements) % 2 != 0:
            raise ReplacementFormatError("Bad code replacements")
        old_code = code_source(func)
        new_code = old_code
        for i in range(0, len(replacements), 2):
            new_code = new_code.replace(replacements[i], replacements[i+1])
        patchy.replace(func, old_code, new_code)


@cache
def code_replace_lines(func, *replacements):
    """
    Additional replace function to allow replacing only specific lines in the
     code of a function.
    
    :param func: function object to be modified
    :param replacements: list of replacements - pairs (str_to_repl, replac)
    """
    r = replacements
    if len(r) % 2 != 0 or not \
        all(isinstance(r[i], int) and (isinstance(r[i+1], string_types) or \
            r[i+1] is None) for i in range(0, len(r), 2)):
        raise ReplacementFormatError("Bad code replacements")
    old_code = code_source(func)
    new_code = old_code.splitlines()
    delete = []
    for i in range(0, len(r), 2):
        n, replacement = r[i:i+2]
        if replacement is None:
            delete.append(n)
        else:
            indent = new_code[n][:len(new_code[n])-len(new_code[n].lstrip())]
            new_code[n] = indent + replacement.lstrip()
    for i in sorted(delete, reverse=True):
        del new_code[i]
    patchy.api._set_source(func, "\n".join(new_code))


def code_restore(func):
    """
    Additional function to restore mofidied code.
    
    :param func: function object to be restored
    :return:     True if function's code was restored
    """
    old_code = __orig_code.get(func)
    if old_code is not None:
        patchy.api._set_source(func, patchy.api.dedent(old_code))
        __old_code[func] = deque([], N_MODIF)
        return True
    return False


def code_revert(func):
    """ 
    Additional function to revert mofidied code to last modification.
    
    :param func: function object to be reverted to last version
    :return:     True if function's code was reverted to last version
    """
    try:
        old_code = __old_code.get(func).pop()
        if old_code is not None:
            patchy.api._set_source(func, patchy.api.dedent(old_code))
            return True
    except:
        return False


def code_source(func):
    """ 
    Alias function to get function's code.
    
    :param func: function object
    :return:     function's source code
    """
    return patchy.api._get_source(func)


# disable source AST check to avoid Python compatibility errors
code_replace(patchy.api._assert_ast_equal,
             "current_ast = ast.parse",
             "return #current_ast = ast.parse",
             cache=False)
