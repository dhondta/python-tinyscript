# -*- coding: UTF-8 -*-
"""Module for enhancing code preimport.

"""
import code
import patchy
import types
from collections import deque
from functools import wraps
from six import string_types


BLOCK_KW = ["class", "def", "elif", "else", "except", "finally", "for", "if", "try", "while", "with"]
N_MODIF  = 3

is_function  = lambda f: isinstance(f, types.FunctionType)
is_method    = lambda f: isinstance(f, types.MethodType)

code.patch   = patchy.patch
code.unpatch = patchy.unpatch
code.Patch   = patchy.temp_patch 


__orig_code = {}
__old_code = {}


class PatchError(ValueError):
    pass
code.PatchError = PatchError


def __apply_code(func, old_code, new_code):
    """ Apply the new code in the given function object. """
    new_code = "\n".join(new_code)
    try:
        patchy.api._set_source(func, new_code)
    except (IndentationError, SyntaxError) as e:
        raise PatchError(e)
    return old_code != new_code


def __get_indent_chars(code_lines):
    """ Guess the indentation characters used in the given code. """
    prev, new = 0, 0
    n, l2 = len(code_lines) - 1, ""
    while prev <= new and n >= 0:
        l1, l2 = l2, code_lines[n]
        indent = l2[:len(l2)-len(l2.lstrip())]
        prev = new
        new = len(indent) if len(l2.strip()) == 0 or not l2.lstrip().startswith("#") else prev
        n -= 1
    return l1[new:prev]
    

def __get_block_indent(code_lines, n):
    """ Guess the indentation level used in the given code from line n. """
    n %= len(code_lines)
    code_lines[n]  # this will raise an error if n too high
    n -= 1
    l = code_lines[n].split("#", 1)[0].rstrip()  # remove comment
    # find the first previous line which is not empty
    while l.strip() == "" and n >= 0:
        n -= 1
        l = code_lines[n].split("#", 1)[0].rstrip()  # remove comment
    indent = l[:len(l) - len(l.lstrip())]
    # if a block keyword is present, return block's indentation ; otherwise,
    #  return the same indentation
    return indent + __get_indent_chars(code_lines) if any(l.lstrip().startswith(kw) for kw in BLOCK_KW) else indent


def __sort_int_text_pairs(text, lst, item):
    """ Check that l only consists of flattened (int, str or None) pairs and that integers are within the range of the
         input text. Then output the list of sorted pairs. """
    l = len(text.split("\n"))
    s = "Bad code {}s".format(item)
    if len(lst) % 2 != 0:
        raise PatchError(s)
    # check the input list based on multiple criteria
    d = {}
    for i in range(0, len(lst), 2):
        n = lst[i]
        # check for inconsistent index
        if not isinstance(n, int):
            raise PatchError(s + " (bad index {})".format(n))
        n = lst[i] if lst[i] >= 0 else lst[i] + l
        # check for out-of-bound values
        if not 0 <= n < l:
            raise PatchError(s + " (invalid index {})".format(n))
        # check for doubles
        if d.get(n) is not None:
            raise PatchError(s + " (double index {})".format(n))
        # check for inconsistent line
        line = lst[i+1]
        _ = [line, ""][line is None]
        if line is not None and not isinstance(_, string_types):
            raise PatchError(s + " (bad line '{}')".format(line))
        d[n] = line
    # then return the sorted list of pairs
    return sorted(d.items(), reverse=True)


def __validate(f):
    """ Simple validation for validating that the input is a function. """
    if not is_function(f) and not is_method(f):
        raise ValueError("{} is not a function".format(f))


def _cache(f):
    """ Decorator for caching code changes locally inside the module. """
    @wraps(f)
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


def code_add_block(func, index, block, after=False):
    """
    Additional modification function to allow adding a block of code at a specific place in the code of a function. The
     input block is automatically reindented relatively to its insertion position. Therefore, successive distinct blocks
     of code with dedented levels SHALL NOT be added in the same block value through this function but well separately.
    
    :param func:  function object to be modified
    :param index: position where the block of code is to be added
    :param block: block of code indented relatively to the insertion position
    :param after: add line after the given index, not before
    :return:      whether code was modified or not
    """
    __validate(func)
    # make the new code
    old_code = code_source(func)
    new_code = old_code.splitlines()
    if after:
        index += 1
    indent = __get_block_indent(new_code, index)
    for line in block.splitlines()[::-1]:
        new_code.insert(index, indent + line)
    return __apply_code(func, old_code, new_code)
code.add_block = code.insert_block = code_add_block


def code_add_line(func, index, addition, **kwargs):
    """
    Alias for applying a single-line addition.
    """
    __validate(func)
    return code_add_lines(func, index, addition, **kwargs)
code.add_line = code.insert_line = code_add_line


@_cache
def code_add_lines(func, *additions, **kwargs):
    """
    Additional modification function to allow adding lines at specific places in the code of a function.
    
    :param func:      function object to be modified
    :param additions: list of additions - pairs (line_index, new_line)
    :param after:     add line after the given index, not before
    :return:          whether code was modified or not
    """
    __validate(func)
    after = kwargs.pop("after", False)
    old_code = code_source(func)
    new_code = old_code.splitlines()
    for n, a in __sort_int_text_pairs(old_code, additions, "addition"):
        if after:
            n += 1
        if n == 0:
            new_code.insert(0, a.lstrip())
        else:
            # automatically compute indentation if not provided in added line
            if len(a) == len(a.lstrip()):
                a = __get_block_indent(new_code, n) + a
            new_code.insert(n, a)
    return __apply_code(func, old_code, new_code)
code.add_lines = code.insert_lines = code_add_lines


def code_delete_line(func, index):
    """
    Alias for applying a single-line removal.
    """
    __validate(func)
    return code_delete_lines(func, index)
code.delete_line = code.remove_line = code_delete_line


def code_delete_lines(func, *indices):
    """
    Additional function to allow deleting only specific lines in the code of a function.
    
    :param func:    function object to be modified
    :param indices: list of line indices for removal
    :return:        whether code was modified or not
    """
    __validate(func)
    replacements = []
    for i in indices:
        replacements.extend([i, None])
    return code_replace_lines(func, *replacements)
code.delete_lines = code.remove_lines = code_delete_lines


@_cache
def code_replace(func, *replacements):
    """
    Slight modification to original replace function to allow replacing only part(s) of code and not necessarily using
     whole function's code.
    
    :param func:         function object to be modified
    :param replacements: list of replacements - pairs (str_to_repl, replac)
    :return:             whether code was modified or not
    """
    __validate(func)
    try:
        patchy.replace(func, *replacements)
        old_code, new_code = replacements
    # if normal handling fails, get whole function's code first, apply replacement then retry
    except:
        if len(replacements) % 2 != 0:
            raise PatchError("Bad code replacement")
        old_code = code_source(func)
        new_code = old_code
        for i in range(0, len(replacements), 2):
            new_code = new_code.replace(replacements[i], replacements[i+1])
        patchy.replace(func, old_code, new_code)
    # report whether the code was changed or not
    return old_code != new_code
code.replace = code_replace


def code_replace_line(func, index, replacement):
    """
    Alias for applying a single-line replacement.
    """
    __validate(func)
    return code_replace_lines(func, index, replacement)
code.replace_line = code_replace_line


@_cache
def code_replace_lines(func, *replacements):
    """
    Additional replace function to allow replacing only specific lines in the code of a function.
    
    :param func:         function object to be modified
    :param replacements: list of replacements - pairs (line_index, replac)
    :return:             whether code was modified or not
    """
    __validate(func)
    r = replacements
    old_code = code_source(func)
    new_code = old_code.splitlines()
    for n, r in __sort_int_text_pairs(old_code, replacements, "replacement"):
        if r is None:
            new_code.pop(n)
        else:
            l = new_code[n]
            indent = l[:len(l)-len(l.lstrip())]
            new_code[n] = indent + r.lstrip()
    return __apply_code(func, old_code, new_code)
code.replace_lines = code_replace_lines


def code_restore(func):
    """
    Additional function to restore mofidied code.
    
    :param func: function object to be restored
    :return:     True if function's code was restored
    """
    __validate(func)
    old_code = __orig_code.get(func)
    if old_code is not None:
        patchy.api._set_source(func, patchy.api.dedent(old_code))
        __old_code[func] = deque([], N_MODIF)
        return True
    return False
code.restore = code_restore


def code_revert(func):
    """ 
    Additional function to revert mofidied code to last modification.
    
    :param func: function object to be reverted to last version
    :return:     True if function's code was reverted to last version
    """
    __validate(func)
    try:
        old_code = __old_code.get(func).pop()
        if old_code is not None:
            patchy.api._set_source(func, patchy.api.dedent(old_code))
            return True
    except:
        return False
code.revert = code_revert


def code_source(func):
    """ 
    Alias function to get function's code.
    
    :param func: function object
    :return:     function's source code
    """
    __validate(func)
    return patchy.api._get_source(func)
code.source = code_source


# disable source AST check to avoid Python compatibility errors
code_replace(patchy.api._assert_ast_equal, "current_ast = ast.parse", "return #current_ast = ast.parse", cache=False)

