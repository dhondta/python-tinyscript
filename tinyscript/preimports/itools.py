# -*- coding: UTF-8 -*-
"""Module for enhancing itertools preimport.

"""
import itertools
from functools import update_wrapper, wraps

from ..helpers.data.types import is_generator, is_generatorfunc


__generator_inputs = {}


class NonResettableGeneratorException(Exception):
    pass
itertools.NonResettableGeneratorException = NonResettableGeneratorException


def __product_lazy(*generators):
    """ This recursive function allows to yield an output of the cartesian product of iterables and generators. """
    gen = (_ for _ in generators[0]) if not is_generator(generators[0]) else reset(generators[0], True)
    for i in gen:
        if len(generators) == 1:
            yield [i]
            continue
        for j in __product_lazy(*generators[1:]):
            yield [i] + j


def product_lazy(*items, **kwargs):
    """ This function can use iterables and generators to generate and output as itertools.product but fully lazy.
    
    :param items:  list of iterables and/or generators
    :param repeat: number of times items should be repeated
    """
    repeat = kwargs.get('repeat', 1)
    if repeat < 0:
        raise ValueError("Repeat must be a positive integer")
    elif repeat == 0:
        # even if 0 occurrence must be generated, trigger the generators
        for i in items:
            if is_generator(i):
                next(i)
        yield ()
    else:
        new_items = []
        for n in range(repeat):
            for i in items:
                if n > 0 and is_generator(i):
                    # make n different instances of the same generator
                    f, args, kwargs = __generator_inputs[i]
                    i = f(*args, **kwargs)
                    __generator_inputs[i] = f, args, kwargs
                new_items.append(i)
        for out in __product_lazy(*new_items):
            yield tuple(out)
itertools.product2 = product_lazy


def reset(g, keep=False):
    """ This function resets a generator to its initial state as of the registered arguments. """
    try:
        f, args, kwargs = __generator_inputs.pop(g) if not keep else __generator_inputs[g]
        return resettable(f)(*args, **kwargs)
    except KeyError:
        raise NonResettableGeneratorException("Cannot reset this generator")
itertools.reset = reset


def resettable(f):
    """ This decorator registers for a generator instance its function and arguments so that it can be reset. """
    if not is_generatorfunc(f):
        raise ValueError("The input function does not produce a generator")
    @wraps(f)
    def _wrapper(*args, **kwargs):
        g = f(*args, **kwargs)
        __generator_inputs[g] = (f, args, kwargs)
        return g
    return _wrapper
itertools.resettable = resettable

