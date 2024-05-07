# -*- coding: UTF-8 -*-
"""Common checking functions and argument types.

"""
from collections.abc import Iterable

from .strings import _str2list
from ....preimports import inspect, types


__all__ = __features__ = []


# various object type check functions
__all__ += ["is_bool", "is_dict", "is_float", "is_int", "is_int_range", "is_list", "is_neg_float", "is_neg_int",
            "is_percentage", "is_pos_float", "is_pos_int", "is_prime"]
is_bool       = lambda b: isinstance(b, bool)
is_dict       = lambda d: isinstance(d, dict)
is_float      = lambda f: isinstance(f, float)
is_int        = lambda i: isinstance(i, int)
is_int_range  = lambda i, i1, i2=None: all(is_int(x) for x in [i, i1, i2 or 0]) and i in (range(i1+1) if i2 is None \
                                                                                          else range(i1, i2+1))
is_list       = lambda l: isinstance(l, (list, set, tuple))
is_neg_float  = lambda f, zero=False: is_float(f) and (f <= 0. if zero else f < 0.)
is_neg_int    = lambda i, zero=False: is_int(i) and (i <= 0 if zero else i < 0)
is_percentage = lambda f: isinstance(f, (int, float)) and 0. <= float(f) <= 1.
is_pos_float  = lambda f, zero=False: is_float(f) and (f >= 0. if zero else f > 0.)
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
__all__ += ["floats", "int_range", "ints", "ints_range", "neg_float", "neg_floats", "negative_float", "negative_floats",
            "neg_int", "neg_ints", "negative_int", "negative_ints", "pos_float", "pos_floats", "positive_float",
            "positive_floats", "pos_int", "positive_int", "pos_ints", "positive_ints", "prime_number", "values_list"]


def __n(ntype):
    def _wrapper(l, check_func=lambda x: False, idescr=None, shouldbe=None, **kwargs):
        """ Parses a comma-separated list of ints. """
        l = _str2list(l)
        if not all(check_func(x, **kwargs) for x in l):
            msg = f"{['Bad list of', 'Not a'][len(l) == 1]} {'' if idescr is None else idescr + ' '}{ntype}" \
                  f"{['s', ''][len(l) == 1]}"
            if shouldbe is not None:
                msg += f" (should be {shouldbe})"
            raise ValueError(msg)
        return l
    return _wrapper

floats = lambda l: __n("float")(l, is_float)
negative_float = neg_float = lambda i, zero=False: __n("float")(i, is_neg_float, "negative", zero=zero)[0]
positive_float = pos_float = lambda i, zero=True: __n("float")(i, is_pos_float, "positive", zero=zero)[0]
negative_floats = neg_floats = lambda l, zero=False: __n("float")(l, is_neg_float, "negative", zero=zero)
positive_floats = pos_floats = lambda l, zero=True: __n("float")(l, is_pos_float, "positive", zero=zero)
floats.__name__ = "floats"
negative_float.__name__  = neg_float.__name__  = "negative float"
negative_floats.__name__ = neg_floats.__name__ = "negative floats list"
positive_float.__name__  = pos_float.__name__  = "positive float"
positive_floats.__name__ = pos_floats.__name__ = "positive floats list"

ints = lambda l: __n("integer")(l, is_int)
int_range = lambda i, i1, i2=None: __n("integer")(i, is_int_range, "valid", "in range [%d,%d]" % \
                                                  (0 if i2 is None else i1, i1 if i2 is None else i2), i1=i1, i2=i2)[0]
negative_int = neg_int = lambda i, zero=False: __n("integer")(i, is_neg_int, "negative", zero=zero)[0]
positive_int = pos_int = lambda i, zero=True: __n("integer")(i, is_pos_int, "positive", zero=zero)[0]
ints_range = lambda l, i1, i2=None: __n("integer")(l, is_int_range, "valid", "in range [%d,%d]" % \
                                                   (0 if i2 is None else i1, i1 if i2 is None else i2), i1=i1, i2=i2)
negative_ints = neg_ints = lambda l, zero=False: __n("integer")(l, is_neg_int, "negative", zero=zero)
positive_ints = pos_ints = lambda l, zero=True: __n("integer")(l, is_pos_int, "positive", zero=zero)
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

