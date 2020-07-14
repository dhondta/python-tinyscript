# -*- coding: UTF-8 -*-
"""Module for enhancing re preimport.

"""
import random
import re
from functools import reduce
from string import *

from .itools import itertools
from ..helpers.attack import MASKS
from ..helpers.compat import b
from ..helpers.constants import PYTHON2
from ..helpers.data.types import is_generator, is_iterable


CATEGORIES = {
    'digit':     digits,
    'not_digit': reduce(lambda x, c: x.replace(c, ""), digits, printable),
    'space':     whitespace,
    'not_space': reduce(lambda x, c: x.replace(c, ""), whitespace, printable),
    'word':      ascii_letters + digits + '_',
    'not_word':  reduce(lambda x, c: x.replace(c, ""), ascii_letters + digits + '_', printable),
}
MAX_REPEAT = 10


@itertools.resettable
def __gen_str_from_re(regex, max_repeat, any_set, rand=False, parsed=False, groups=dict()):
    """ Recursive function to generate strings from a regex pattern. """
    if regex is None:
        return
    tokens = []
    negate = False
    for state in (regex if parsed else re.sre_parse.parse(b(getattr(regex, "pattern", regex)))):
        code = getattr(state[0], "name", state[0]).lower()
        value = getattr(state[1], "name", state[1])
        value = value.lower() if isinstance(value, str) else value
        if code in ["assert_not", "at"]:
            continue
        elif code == "any":
            charset = any_set.replace("\n", "")  # this assumes !re.DOTALL
            tokens.append(random.choice(charset) if rand else charset)
        elif code == "assert":
            tokens.append(__gen_str_from_re(value[1], max_repeat, any_set, rand, True, groups))
        elif code == "branch":
            result = []
            for r in value[1]:
                result += __gen_str_from_re(r, max_repeat, any_set, rand, True, groups)
            tokens.append(result)
        elif code == "category":
            charset = CATEGORIES[value[9:]]
            if negate:
                negate = False
                charset = set(any_set).difference(charset)
            tokens.append(random.choice(charset) if rand else charset)
        elif code == "groupref":
            # nested generator for handling registered group expression
            @itertools.resettable
            def group_gen(v):
                for c in itertools.product2(groups[v]):
                    yield "".join(c)
            tokens.append(group_gen(value))
        elif code == "in":
            # note: this state generates the full list of possible characters from a set, e.g. [A-Z], there shouldn't be
            #        any valid regex-related case that allows to put a subpattern therein ; therefore, non-lazily nature
            #        is not an issue here
            charset = [x for l in __gen_str_from_re(value, max_repeat, any_set, rand, True, groups) for x in l]
            tokens.append(random.choice(charset) if rand else charset)
            # example: r"[ab]" will be state [(LITERAL, 97), (LITERAL, 98)], that converts to ['a', 'b']
        elif code == "literal":
            tokens.append(chr(value))
        elif code in ["max_repeat", "min_repeat"]:
            start, end = value[:2]
            end = max_repeat if getattr(end, "name", str(end)).lower() == "maxrepeat" else end
            end = min(end, max_repeat)
            start = min(start, end)
            # nested generator for handling repeated expressions, e.g. (|[A-Z][a-z]*|tests?){0,5}
            #                                                                      ^      ^   ^
            #                                                                      1      2   3
            # 1: star repeat ; this will be limited to 'max_repeat' that defaults to MAX_REPEAT
            # 2: case where start=0 and end=1
            # 3: explicit repeat
            @itertools.resettable
            def repeat_gen(v):
                empty_yield = False
                for n in ([random.randint(start, end + 1)] if rand else range(start, end + 1)):
                    charset = __gen_str_from_re(v[-1], max_repeat, any_set, rand, True, groups)
                    for c in itertools.product2(charset, repeat=n):
                        r = "".join(c)
                        # yield empty string only once ; otherwise e.g. (|test){0,5} would yield 6x ""
                        if len(r) == 0:
                            if not empty_yield:
                                empty_yield = True
                                yield ""
                        else:
                            yield r
            tokens.append(repeat_gen(value))
        elif code == "negate":
            negate = True
        elif code == "not_literal":
            charset = any_set.replace(chr(value), "")
            tokens.append(random.choice(charset) if rand else charset)
        elif code == "range":
            charset = "".join(chr(i) for i in range(value[0], value[1] + 1))
            tokens.append(random.choice(charset) if rand else charset)
        elif code == "subpattern":
            result = __gen_str_from_re(value[-1], max_repeat, any_set, rand, True, groups)
            if value[0]:
                groups[value[0]] = result
            tokens.append(result)
        else:
            raise NotImplementedError("Unhandled code '{}'".format(code))
    if len(tokens) == 0:
        tokens = [[""]]
    for result in itertools.product2(*tokens):
        yield "".join(result)


def __get_re_size(regex, max_repeat, any_set, parsed=False, groups=dict()):
    """ Recursive function to get the size of the set of strings generated by a regex pattern. """
    if regex is None:
        return 0
    result = 1
    negate = False
    for state in (regex if parsed else re.sre_parse.parse(b(getattr(regex, "pattern", regex)))):
        code = getattr(state[0], "name", state[0]).lower()
        value = getattr(state[1], "name", state[1])
        value = value.lower() if isinstance(value, str) else value
        if code in ["assert_not", "at", "literal"]:
            continue
        elif code == "any":
            result *= len(any_set.replace("\n", ""))  # this assumes !re.DOTALL
        elif code == "assert":
            result *= __get_re_size(value[1], max_repeat, any_set, True, groups)
        elif code == "branch":
            n = 0
            for r in value[1]:
                n += __get_re_size(r, max_repeat, any_set, True, groups)
            result *= n
        elif code == "category":
            charset = CATEGORIES[value[9:]]
            if negate:
                negate = False
                charset = set(any_set).difference(charset)
            result *= len(charset)
        elif code == "groupref":
            result *= groups[value]
        elif code == "in":
            # if all codes are literals, we have a set of characters whose length is simply the number of literals
            if all(getattr(st[0], "name", st[0]).lower() == "literal" for st in value):
                result *= len(value)
            # otherwise, we shall recurse
            else:
                result *= __get_re_size(value, max_repeat, any_set, True, groups)
        elif code in ["max_repeat", "min_repeat"]:
            start, end = value[:2]
            end = max_repeat if getattr(end, "name", str(end)).lower() == "maxrepeat" else end
            end = min(end, max_repeat)
            start = min(start, end)
            if end == float("inf") or PYTHON2 and end == 4294967295:
                return float("inf")
            n = __get_re_size(value[-1], max_repeat, any_set, True, groups)
            k, empty_yield = 0, False
            for r in range(start, end + 1):
                if r == 0:
                    empty_yield = True
                # tricky case: (|[0-5])? and ([0-5])? give the same outputs, however re.size will give respectively
                #                  8     and    7   ; why ? because the output value "" is filtered in re.strings
                # so, we need to handle this special case by substracting 1 when we have:
                # - a subpattern (...)
                # - with a branch ...|...
                # e.g. [(SUBPATTERN, (1, 0, 0, [(BRANCH, (None, [[], [(IN, [(RANGE, (48, 53))])]]))]))]
                #                                                ^
                elif empty_yield:
                    try:
                        if any(len(x) == 0 for x in value[-1][0][-1][-1][0][-1][-1]):
                            #                                \_____/\_____________/
                            k -= 1  #       subpattern's value _/          \_ branch's list of values
                    except (IndexError, TypeError):
                        pass
                k += n ** r
            result *= k
        elif code == "negate":
            negate = True
        elif code == "not_literal":
            result *= len(any_set.replace(chr(value), ""))
        elif code == "range":
            result *= len("".join(chr(i) for i in range(value[0], value[1] + 1)))
        elif code == "subpattern":
            n = __get_re_size(value[-1], max_repeat, any_set, True, groups)
            if value[0]:
                groups[value[0]] = n
            result *= n
        else:
            raise NotImplementedError("Unhandled code '{}'".format(code))
    return result


__set_any = lambda s: MASKS[s] if s in MASKS.keys() else s or printable
__set_max = lambda m: float(m) if m == "inf" else m


def _generate_random_string_from_regex(regex, max_repeat=MAX_REPEAT, any_set=None):
    """ Utility function to generate a single random string from a regex pattern. """
    return next(__gen_str_from_re(regex, __set_max(max_repeat), __set_any(any_set), rand=True))
re.randstr = _generate_random_string_from_regex


def _generate_random_strings_from_regex(regex, n=10, max_repeat=MAX_REPEAT, any_set=None):
    """ Utility function to generate a single random string from a regex pattern. """
    for i in range(n):
        yield next(__gen_str_from_re(regex, __set_max(max_repeat), __set_any(any_set), rand=True))
re.randstrs = _generate_random_strings_from_regex


def _generate_all_strings_from_regex(regex, max_repeat=MAX_REPEAT, any_set=None):
    """ Utility function to generate all possible strings from a regex pattern. """
    for result in __gen_str_from_re(regex, __set_max(max_repeat), __set_any(any_set)):
        yield result
re.strings = _generate_all_strings_from_regex


def _get_size_of_regex(regex, max_repeat=MAX_REPEAT, any_set=None):
    """ Utility function to get the number of all possible strings from a regex pattern. """
    return __get_re_size(regex, __set_max(max_repeat), __set_any(any_set))
re.size = _get_size_of_regex

