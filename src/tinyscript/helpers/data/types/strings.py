# -*- coding: UTF-8 -*-
"""String-related checking functions and argument types.

"""
from six import binary_type, string_types

from ....preimports import ast, re, string


__all__ = __features__ = []


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


def _is_from_alph(s, a, t):
    if is_str(s):
        val = str_contains(a, t)
        try:
            val(s)
            return True
        except ValueError:
            pass
    return False


# various string-related check functions
__all__ += ["is_str", "is_bytes", "is_digits", "is_letters", "is_lowercase", "is_printable", "is_punctuation",
            "is_uppercase"]
is_str         = lambda s: isinstance(s, string_types)
is_bytes       = lambda s: isinstance(s, binary_type)
is_digits      = lambda s, t=1.0: _is_from_alph(s, string.digits, t)
is_letters     = lambda s, t=1.0: _is_from_alph(s, string.ascii_letters, t)
is_lowercase   = lambda s, t=1.0: _is_from_alph(s, string.ascii_lowercase, t)
is_printable   = lambda s, t=1.0: _is_from_alph(s, string.printable, t)
is_punctuation = lambda s, t=1.0: _is_from_alph(s, string.punctuation, t)
is_uppercase   = lambda s, t=1.0: _is_from_alph(s, string.ascii_uppercase, t)
is_str.__name__         = "string"
is_bytes.__name__       = "bytes"
is_digits.__name__      = "digits"
is_letters.__name__     = "letters"
is_lowercase.__name__   = "lowercase string"
is_printable.__name__   = "printable string"
is_punctuation.__name__ = "punctuation"
is_uppercase.__name__   = "uppercase string"

# various data format check functions
__all__ += ["is_bin", "is_hex"]
is_bin = lambda b: is_str(b) and all(set(_).difference(set("01")) == set() for _ in re.split(r"\W+", b)) or \
                   isinstance(b, (list, set, tuple)) and all(str(x) in "01" for x in b)
is_hex = lambda h: is_str(h) and len(h) % 2 == 0 and set(h.lower()).difference(set("0123456789abcdef")) == set()
is_bin.__name__ = "binary string"
is_hex.__name__ = "hexadecimal string"

# some other common check functions
__all__ += ["is_long_opt", "is_short_opt"]
is_long_opt  = lambda o: is_str(o) and re.match(r"^--[a-z]+(-[a-z]+)*$", o, re.I)
is_short_opt = lambda o: is_str(o) and re.match(r"^-[a-z]$", o, re.I)

# another useful check function
__all__ += ["is_regex", "regular_expression"]
is_regex = lambda s: __regex(s, False) is not None


def __regex(regex, fail=True):
    """ Regular expression validation. """
    try:
        re.sre_parse.parse(regex)
        return regex
    except re.sre_parse.error:
        if fail:
            raise ValueError("Bad regular expression")
regular_expression = lambda s: __regex(s)
regular_expression.__name__ = "regular expression"


# -------------------- STRING FORMAT ARGUMENT TYPES --------------------
__all__ += ["str_contains", "str_matches"]


def str_contains(alphabet, threshold=1.0):
    """ Counts the characters of a string and determines, given an alphabet, if the string has enough valid characters.
    """
    if not 0.0 < threshold <= 1.0:
        raise ValueError("Bad threshold (should be between 0 and 1)")
    def _validation(s):
        p = sum(int(c in alphabet) for c in s) / float(len(s))
        if p < threshold:
            raise ValueError("Input string does not contain enough items from the given alphabet ({:.2f}%)"
                             .format(p * 100))
        return s
    _validation.__name__ = "string contained"
    return _validation


def str_matches(pattern, flags=0):
    """ Applies the given regular expression to a string argument. """
    def _validation(s):
        if re.match(pattern, s, flags) is None:
            raise ValueError("Input string does not match the given regex")
        return s
    _validation.__name__ = "string match"
    return _validation

