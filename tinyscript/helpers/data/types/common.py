# -*- coding: UTF-8 -*-
"""Common checking functions and argument types.

"""
import ast
import re
from six import string_types


__all__ = __features__ = []

try:
    long
except NameError:
    long = int


# various object type check functions
__all__ += ["is_dict", "is_function", "is_int", "is_lambda", "is_list",
            "is_neg_int", "is_pos_int", "is_str"]
is_int      = lambda i: isinstance(i, (int, long))
is_pos_int  = lambda i, zero=True: is_int(i) and (i >= 0 if zero else i > 0)
is_neg_int  = lambda i, zero=False: is_int(i) and (i <= 0 if zero else i < 0)
is_dict     = lambda d: isinstance(d, dict)
is_list     = lambda l: isinstance(l, (list, set, tuple))
is_str      = lambda s: isinstance(s, string_types)
is_lambda   = lambda l: isinstance(l, type(lambda:0)) and \
                        l.__name__ == (lambda:0).__name__
is_function = lambda f: hasattr(f, "__call__")

# various data format check functions
__all__ += ["is_bin", "is_hex"]
is_bin = lambda b: is_str(b) and all(set(_).difference(set("01")) == set() \
                                     for _ in re.split(r"\W+", b))
is_hex = lambda h: is_str(h) and len(h) % 2 == 0 and \
                   set(h.lower()).difference(set("0123456789abcdef")) == set()

# some other common check functions
__all__ += ["is_long_opt", "is_short_opt"]
is_long_opt  = lambda o: is_str(o) and \
                         re.match(r"^--[a-z]+(-[a-z]+)*$", o, re.I)
is_short_opt = lambda o: is_str(o) and re.match(r"^-[a-z]$", o, re.I)


def _str2list(s):
    """ Convert string to list if input is effectively a string. """
    # if already a list, simply return it, otherwise ensure input is a string
    if isinstance(s, list):
        return s
    else:
        s = str(s)
    # remove heading and trailing brackets
    if s[0] == '[' and s[-1] == ']' or s[0] == '(' and s[-1] == ')':
        s = s[1:-1]
    # then parse list elements from the string
    l = []
    for i in s.split(","):
        i = i.strip()
        try:
            l.append(ast.literal_eval(i))
        except Exception:
            l.append(i)
    return l


# -------------------- DATA FORMAT ARGUMENT TYPES --------------------
__all__ += ["neg_int", "negative_int", "pos_int", "positive_int", "ints",
            "neg_ints", "negative_ints", "pos_ints", "positive_ints",
            "str_matches"]


def __ints(l, check_func=lambda x: False, idescr=None, **kwargs):
    """ Parses a comma-separated list of ints. """
    l = _str2list(l)
    msg = "{} {}integer{}".format(["Bad list of", "Not a"][len(l) == 1],
                                  "" if idescr is None else idescr + " ",
                                  ["s", ""][len(l) == 1])
    if not all(check_func(_, **kwargs) for _ in l):
        raise ValueError(msg)
    return l
ints = lambda l: __ints(l, is_int)
negative_int = neg_int = \
    lambda i, zero=False: __ints(i, is_neg_int, "negative", zero=zero)[0]
positive_int = pos_int = \
    lambda i, zero=True: __ints(i, is_pos_int, "positive", zero=zero)[0]
negative_ints = neg_ints = \
    lambda l, zero=False: __ints(l, is_neg_int, "negative", zero=zero)
positive_ints = pos_ints = \
    lambda l, zero=True: __ints(l, is_pos_int, "positive", zero=zero)


def str_matches(pattern, flags=0):
    """ Applies the given regular expression to a string argument. """
    def _validation(s):
        if re.match(pattern, s, flags) is None:
            raise ValueError("Input string does not match the given regex")
        return s
    return _validation
