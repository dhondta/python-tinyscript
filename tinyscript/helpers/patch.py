#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Useful functions for runtime code patching.

"""
import patchy
from collections import deque
from six import string_types


__all__ = __features__ = ["code_patch", "code_unpatch", "CodePatch",
                          "code_add_line", "code_add_lines",
                          "code_delete_line", "code_delete_lines",
                          "code_remove_line", "code_remove_lines",
                          "code_replace", "code_replace_line",
                          "code_replace_lines", "code_restore", "code_revert",
                          "code_source"]


BLOCK_KW = ["class", "def", "elif", "else", "except", "finally", "for", "if",
            "try", "while", "with"]
N_MODIF  = 3


code_patch   = patchy.patch
code_unpatch = patchy.unpatch
CodePatch    = patchy.temp_patch 


__orig_code = {}
__old_code = {}


class PatchError(ValueError):
    pass


def __get_indent_chars(code_lines):
    prev, new = 0, 0
    n, l2 = len(code_lines) - 1, ""
    while prev <= new and n >= 0:
        l1, l2 = l2, code_lines[n]
        indent = l2[:len(l2)-len(l2.lstrip())]
        prev = new
        new = len(indent) if len(l2.strip()) == 0 or \
                             not l2.lstrip().startswith("#") else prev
        n -= 1
    return l1[new:prev]
    

def __get_block_indent(code_lines, n):
    n %= len(code_lines)
    code_lines[n]  # this will raise an error if n too high
    n -= 1
    l = code_lines[n].split("#", 1)[0].rstrip()  # remove comment
    # find the first previous line which is not empty
    while l.strip() == "" and n >= 0:
        n -= 1
        l = code_lines[n].split("#", 1)[0].rstrip()  # remove comment
    indent = l[:len(l) - len(l.lstrip())]
    # if a block keyword is present, return block's indentation
    if any(l.lstrip().startswith(kw) for kw in BLOCK_KW):
        return indent + __get_indent_chars(code_lines)
    # else, return same indentation
    return indent


def cache(f):
    def _wrapper(*args, **kwargs):
        cache = kwargs.pop("cache", True)
        if cache:
            func = args[0]
            old_code = code_source(func)
        f(*args, **kwargs)
        if cache:
            if __orig_code.get(func) is None:
                __orig_code[func] = old_code
            if __old_code.get(func) is None:
                __old_code[func] = deque([], N_MODIF)
            __old_code[func].append(old_code)
    return _wrapper


def code_add_line(func, index, addition, **kwargs):
    """
    Alias for applying a single-line addition.
    """
    return code_add_lines(func, index, addition, **kwargs)


@cache
def code_add_lines(func, *additions, **kwargs):
    """
    Additional modification function to allow adding lines at specific places in
     the code of a function.
    
    :param func:      function object to be modified
    :param additions: list of additions - pairs (line_index, new_line)
    :param after:     add line after the given index, not before
    :return:          whether code was modified or not
    """
    a = additions
    after = kwargs.pop("after", False)
    if len(a) % 2 != 0 or not \
        all(isinstance(a[i], int) and isinstance(a[i+1], string_types) \
            for i in range(0, len(a), 2)):
        raise PatchError("Bad code additions")
    indices = [a[i] for i in range(0, len(a), 2)]
    if len(indices) != len(set(indices)):
        raise PatchError("Bad code replacements")
    old_code = code_source(func)
    new_code = old_code.splitlines()
    a = [(a[i], a[i+1]) for i in range(0, len(a), 2)]
    for i in sorted(a, key=lambda x: x[0], reverse=True):
        n, addition = i
        if after:
            n += 1
        if n == 0:
            new_code.insert(0, addition.lstrip())
        else:
            # automatically compute indentation if not provided in added line
            if len(addition) == len(addition.lstrip()):
                addition = __get_block_indent(new_code, n) + addition
            new_code.insert(n, addition)
    new_code = "\n".join(new_code)
    patchy.api._set_source(func, new_code)
    return old_code != new_code


def code_delete_line(func, index):
    """
    Alias for applying a single-line removal.
    """
    return code_delete_lines(func, index)
code_remove_line = code_delete_line


def code_delete_lines(func, *indices):
    """
    Additional function to allow deleting only specific lines in the code of a
     function.
    
    :param func:    function object to be modified
    :param indices: list of line indices for removal
    :return:        whether code was modified or not
    """
    replacements = []
    for i in indices:
        replacements.extend([i, None])
    return code_replace_lines(func, *replacements)
code_remove_lines = code_delete_lines


@cache
def code_replace(func, *replacements):
    """
    Slight modification to original replace function to allow replacing only
     part(s) of code and not necessarily using whole function's code.
    
    :param func:         function object to be modified
    :param replacements: list of replacements - pairs (str_to_repl, replac)
    :return:             whether code was modified or not
    """
    try:
        patchy.replace(func, *replacements)
        old_code, new_code = replacements
    # if normal handling fails, get whole function's code first, apply
    #  replacement then retry
    except:
        if len(replacements) % 2 != 0:
            raise PatchError("Bad code replacement")
        old_code = code_source(func)
        new_code = old_code
        for i in range(0, len(replacements), 2):
            new_code = new_code.replace(replacements[i], replacements[i+1])
        patchy.replace(func, old_code, new_code)
    return old_code != new_code


def code_replace_line(func, index, replacement):
    """
    Alias for applying a single-line replacement.
    """
    return code_replace_lines(func, index, replacement)


@cache
def code_replace_lines(func, *replacements):
    """
    Additional replace function to allow replacing only specific lines in the
     code of a function.
    
    :param func:         function object to be modified
    :param replacements: list of replacements - pairs (line_index, replac)
    :return:             whether code was modified or not
    """
    r = replacements
    if len(r) % 2 != 0 or not \
        all(isinstance(r[i], int) and (isinstance(r[i+1], string_types) or \
            r[i+1] is None) for i in range(0, len(r), 2)):
        raise PatchError("Bad code replacements")
    indices = [r[i] for i in range(0, len(r), 2)]
    if len(indices) != len(set(indices)):
        raise PatchError("Bad code replacements")
    old_code = code_source(func)
    new_code = old_code.splitlines()
    delete = []
    for i in range(0, len(r), 2):
        n, replacement = r[i:i+2]
        if replacement is None:
            delete.append(n)
        else:
            l = new_code[n]
            indent = l[:len(l)-len(l.lstrip())]
            new_code[n] = indent + replacement.lstrip()
    nref = 0
    for i in sorted(delete, reverse=True):
        if i < 0:
            i = min(-1, nref)
            nref = -i
        del new_code[i]
    new_code = "\n".join(new_code)
    patchy.api._set_source(func, new_code)
    return old_code != new_code


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