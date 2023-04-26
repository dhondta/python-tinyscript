# -*- coding: UTF-8 -*-
"""Common checking functions and argument types.

"""
from six import integer_types
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

from .strings import _str2list
from ....preimports import inspect, types


__all__ = __features__ = []


# various object type check functions
__all__ += ["is_bool", "is_dict", "is_int", "is_int_range", "is_list", "is_neg_int", "is_percentage", "is_pos_int",
            "is_prime"]
is_bool       = lambda b: isinstance(b, bool)
is_dict       = lambda d: isinstance(d, dict)
is_int        = lambda i: isinstance(i, integer_types)
is_int_range  = lambda i, i1, i2=None: all(is_int(x) for x in [i, i1, i2 or 0]) and i in (range(i1+1) if i2 is None \
                                                                                          else range(i1, i2+1))
is_list       = lambda l: isinstance(l, (list, set, tuple))
is_neg_int    = lambda i, zero=False: is_int(i) and (i <= 0 if zero else i < 0)
is_percentage = lambda f: isinstance(f, (int, float)) and 0. <= float(f) <= 1.
is_pos_int    = lambda i, zero=True: is_int(i) and (i >= 0 if zero else i > 0)
is_prime      = lambda i: __prime_number(i)

__all__ += ["is_class", "is_coroutine", "is_coroutinefunc", "is_frame", "is_function", "is_generator",
            "is_generatorfunc", "is_instance", "is_iterable", "is_lambda", "is_method", "is_module", "is_type"]
is_class         = lambda c: inspect.isclass(c)
is_coroutine     = lambda c: inspect.iscoroutine(c)
is_coroutinefunc = lambda c: inspect.iscoroutinefunction(c)
is_frame         = lambda f: isinstance(f, types.FrameType)
is_function      = lambda f, builtin=False: isinstance(f, getattr(types, ["", "Builtin"][builtin] + "FunctionType"))
is_generator     = lambda g: inspect.isgenerator(g)
is_generatorfunc = lambda g: inspect.isgeneratorfunction(g)
is_instance      = lambda i, cls=object: isinstance(i, cls)
is_iterable      = lambda i: isinstance(i, Iterable)
is_lambda        = lambda l: isinstance(l, types.LambdaType)
is_method        = lambda m, builtin=False: isinstance(m, getattr(types, ["", "Builtin"][builtin] + "MethodType"))
is_module        = lambda m: isinstance(m, types.ModuleType)
is_type          = lambda t: isinstance(t, type)


# -------------------- DATA FORMAT ARGUMENT TYPES --------------------
__all__ += ["int_range", "neg_int", "negative_int", "pos_int", "positive_int", "ints", "ints_range", "neg_ints",
            "negative_ints", "pos_ints", "positive_ints", "prime_number", "values_list"]


def __ints(l, check_func=lambda x: False, idescr=None, shouldbe=None, **kwargs):
    """ Parses a comma-separated list of ints. """
    l = _str2list(l)
    msg = "{} {}integer{}".format(["Bad list of", "Not a"][len(l) == 1], "" if idescr is None else idescr + " ",
                                  ["s", ""][len(l) == 1])
    if shouldbe is not None:
        msg += " (should be %s)" % shouldbe
    if not all(check_func(_, **kwargs) for _ in l):
        raise ValueError(msg)
    return l
ints = lambda l: __ints(l, is_int)
int_range = lambda i, i1, i2=None: __ints(i, is_int_range, "valid", "in range [%d,%d]" % \
                                          (0 if i2 is None else i1, i1 if i2 is None else i2), i1=i1, i2=i2)[0]
negative_int = neg_int = lambda i, zero=False: __ints(i, is_neg_int, "negative", zero=zero)[0]
positive_int = pos_int = lambda i, zero=True: __ints(i, is_pos_int, "positive", zero=zero)[0]
ints_range = lambda l, i1, i2=None: __ints(l, is_int_range, "valid", "in range [%d,%d]" % \
                                           (0 if i2 is None else i1, i1 if i2 is None else i2), i1=i1, i2=i2)
negative_ints = neg_ints = lambda l, zero=False: __ints(l, is_neg_int, "negative", zero=zero)
positive_ints = pos_ints = lambda l, zero=True: __ints(l, is_pos_int, "positive", zero=zero)
ints.__name__       = "integers"
int_range.__name__  = "integer (from range)"
ints_range.__name__ = "integers list (from range)"
negative_int.__name__  = neg_int.__name__  = "negative integer"
negative_ints.__name__ = neg_ints.__name__ = "negative integers list"
positive_int.__name__  = pos_int.__name__  = "positive integer"
positive_ints.__name__ = pos_ints.__name__ = "positive integers list"


# see: https://stackoverflow.com/questions/15285534/isprime-function-for-python-language
def __prime_number(n, fail=False):
    """ Determines if a number is a prime. """
    try:
        i = int(n)
        if i != n:
            raise ValueError
    except:
        if fail:
            raise ValueError("Not a prime number")
        return False
    if i in [2, 3, 5, 7]:
        return i if fail else True
    if i < 2 or i % 2 == 0 or i % 3 == 0:
        if fail:
            raise ValueError("Not a prime number")
        return False
    # all primes > 3 are of the form: 6n +/- 1 ; so, start with f = 5 and test f, f+2 for being prime then loop by 6. 
    f, r = 5, int(i ** .5)
    while f <= r:
        if i % f == 0 or i % (f + 2) == 0:
            if fail:
                raise ValueError("Not a prime number")
            return False
        f += 6
    return i if fail else True
prime_number = lambda n: __prime_number(n, True)
prime_number.__name__ = "prime number"


def values_list(var):
    """ Alias to _str2list for use in types of argparse argument.
    
    NB: It converts anything to a list, that is, it never fails. """
    return _str2list(var)

