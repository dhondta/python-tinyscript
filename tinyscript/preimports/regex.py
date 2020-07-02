# -*- coding: UTF-8 -*-
"""Module for enhancing re preimport.

"""
import random
import re
from functools import reduce
from itertools import chain, product
from string import *

from ..helpers.compat import b


CATEGORIES = {
    'digit':     digits,
    'not_digit': reduce(lambda x, c: x.replace(c, ""), digits, printable),
    'space':     whitespace,
    'not_space': reduce(lambda x, c: x.replace(c, ""), whitespace, printable),
    'word':      ascii_letters + digits + '_',
    'not_word':  reduce(lambda x, c: x.replace(c, ""), ascii_letters + digits + '_', printable),
}
GENERATE_MAX  = 20
STAR_PLUS_MAX = 10
YIELD_MAX     = 100


def __gen_str_from_re(regex, star_plus_max, generate_max, yield_max, parsed=False):
    """ Recursive function to generate strings from a regex pattern. """
    if regex is None:
        return
    __groups = {}
    tokens = []
    negate = False
    yield_max = yield_max or -1
    for state in (regex if parsed else re.sre_parse.parse(b(getattr(regex, "pattern", regex)))):
        code = getattr(state[0], "name", state[0]).lower()
        value = getattr(state[1], "name", state[1])
        value = value.lower() if isinstance(value, str) else value
        if code in ["assert_not", "at"]:
            continue
        elif code == "any":
            # should be ord(x) with x belongs to [0, 256[
            tokens.append(__reduce_set(printable.replace("\n", ""), yield_max))
        elif code == "assert":
            result = list(__gen_str_from_re(value[1], star_plus_max, generate_max, yield_max, True))
            tokens.append(__reduce_set(result, yield_max))
        elif code == "branch":
            result = []
            for r in value[1]:
                result += list(__gen_str_from_re(r, star_plus_max, generate_max, yield_max, True)) or [""]
            tokens.append(__reduce_set(result, yield_max))
        elif code == "category":
            charset = CATEGORIES[value[9:]]
            if negate:
                negate = False
                charset = list(set(printable).difference(charset))
            tokens.append(__reduce_set(charset, yield_max))
        elif code == "groupref":
            tokens.extend(__groups[value])
        elif code == "in":
            subtokens = list(__gen_str_from_re(value, star_plus_max, generate_max, yield_max, True))
            subtokens = [x for l in subtokens for x in l]
            tokens.append(__reduce_set(subtokens, yield_max))
        elif code == "literal":
            tokens.append(chr(value))
        elif code in ["max_repeat", "min_repeat"]:
            start, end = value[:2]
            end = min(end, star_plus_max)
            charset = list(__gen_str_from_re(value[-1], star_plus_max, generate_max, yield_max, True))
            subtokens = []
            if start == 0 and end == 1:
                subtokens.append("")
                subtokens.extend(charset)
            elif len(charset) ** end > generate_max > 0:
                for i in range(min(generate_max, 10 * len(charset))):
                    n = random.randint(start, end + 1)
                    token = "" if n == 0 else "".join(random.choice(charset) for _ in range(n))
                    if token not in subtokens:
                        subtokens.append(token)
            else:
                for n in range(start, end + 1):
                    for c in product(charset, repeat=n):
                        subtokens.append("".join(c))
            tokens.append(__reduce_set(subtokens, yield_max))
        elif code == "negate":
            negate = True
        elif code == "not_literal":
            tokens.append(__reduce_set(printable.replace(chr(value), ""), yield_max))
        elif code == "range":
            tokens.append(__reduce_set("".join(chr(i) for i in range(value[0], value[1] + 1)), yield_max))
        elif code == "subpattern":
            result = list(__gen_str_from_re(value[-1], star_plus_max, generate_max, yield_max, True))
            if value[0]:
                __groups[value[0]] = result
            tokens.append(__reduce_set(result, yield_max))
        else:
            raise NotImplementedError("Unhandled code '{}'".format(code))
    if len(tokens) == 0:
        tokens = [""]
    i = 0
    for result in product(*tokens):
        yield "".join(result)
        i += 1
        if i >= yield_max > 0:
            break


def __reduce_set(itemset, yield_max):
    """ Performance optimization function to limit an item set while generating strings from the regex. """
    itemset = list(itemset)
    # if less string instances are required than the length of the given item set, make a new reduced set
    if 0 < yield_max < len(itemset):
        newset = []
        # randomly choose yield_max instances from the item set to reduce the generated lists of possible strings ;
        #  this is particularly useful when subpatterns are used as they must be generated for the product(...) of the
        #  main pattern
        for i in range(yield_max):
            newset.append(itemset.pop(random.randint(0, len(itemset)-1)))
        itemset = newset
    return itemset


def _generate_random_string_from_regex(regex, star_plus_max=STAR_PLUS_MAX, generate_max=GENERATE_MAX):
    """ Utility function to generate a single random string from a regex pattern. """
    return list(__gen_str_from_re(regex, star_plus_max, generate_max, 1))[0]
re.randstr = _generate_random_string_from_regex


def _generate_strings_from_regex(regex, n=YIELD_MAX, star_plus_max=STAR_PLUS_MAX, generate_max=GENERATE_MAX):
    """ Utility function to generate n random strings from a regex pattern. """
    for result in __gen_str_from_re(regex, star_plus_max, generate_max, n):
        yield result
re.randstrs = _generate_strings_from_regex


def _generate_all_strings_from_regex(regex, star_plus_max=STAR_PLUS_MAX, generate_max=GENERATE_MAX):
    """ Utility function to generate all possible strings from a regex pattern. """
    for result in __gen_str_from_re(regex, star_plus_max, -1, -1):
        yield result
re.strings = _generate_all_strings_from_regex

