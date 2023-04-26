# -*- coding: UTF-8 -*-
"""Common utility functions.

"""
from itertools import permutations, product
from string import digits, printable, punctuation

from .compat import b, ensure_str
from .data import is_file, is_list, is_str
from ..preimports import re


__all__ = __features__ = ["bruteforce", "bruteforce_mask", "bruteforce_pin", "bruteforce_re", "dictionary",
                          "expand_mask", "parse_rule"]


MASKS = {
    '*': "".join(chr(i) for i in range(256)),
    '<': "([{<",
    '>': ")]}>",
    'c': "bcdfghjklmnpqrstvwxz",
    'C': "BCDFGHJKLMNPQRSTVWXZ",
    'd': "0123456789",
    'h': "0123456789abcdef",
    'H': "0123456789ABCDEF",
    'l': "abcdefghijklmnopqrstuvwxyz",
    'L': "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    'p': printable,
    's': " " + punctuation,
    'v': "aeiouy",
    'V': "AEIOUY",
}
RULES = {
    'a[]': lambda s: lambda t: t + s,
    'p[]': lambda s: lambda t: s + t,
    'c': lambda t: t.capitalize(),
    'i': lambda t: t,
    'l': lambda t: t.lower(),
    'r': lambda t: t[::-1],
    's': lambda t: t.swapcase(),
    't': lambda t: t.title(),
    'u': lambda t: t.upper(),
}


def bruteforce(maxlen, alphabet=tuple(map(chr, range(256))), minlen=1, repeat=True):
    """ Generator for bruteforcing according to minimum and maximum lengths and an alphabet.
    
    :param maxlen:   maximum bruteforce entry length
    :param alphabet: bruteforce alphabet to be used
    :param minlen:   minimum bruteforce entry length (optional)
    :param repeat:   whether alphabet characters can be repeated or not
    :yield:          bruteforce entry
    """
    if maxlen < 1:
        raise ValueError("Bad bruteforce maximum length")
    if minlen < 0 or minlen > maxlen:
        raise ValueError("Bad bruteforce minimum length")
    for i in range(minlen, maxlen + 1):
        if repeat:
            for c in product(alphabet, repeat=i):
                yield c if isinstance(c[0], int) else ''.join(c)
        else:
            for c in permutations(alphabet, i):
                yield c if isinstance(c[0], int) else ''.join(c)


def bruteforce_mask(mask, charsets=None):
    """ Generator for bruteforcing according to a given mask (mostly similar to this used in hashcat).
    
    :param mask:     bruteforce mask
    :param charsets: custom alphabets for use with the mask
    """
    if is_str(mask):
        mask = expand_mask(mask, charsets)
    if not is_list(mask) or any(not is_str(x) for x in mask):
        raise ValueError("Bad mask ; should be a string or a list of strings, got {}".format(type(mask)))
    for c in product(*mask):
        yield c if isinstance(c[0], int) else ''.join(c)


def bruteforce_pin(length=4):
    """ Generator for bruteforcing a PIN code according to the blog article titled "PIN analysis", available at:
         https://datagenetics.com/blog/september32012/
    Note: This generator generalizes to any length of PIN code.
    
    :param length: PIN code length
    """
    if length <= 0:
        raise ValueError("Bad PIN code length")
    
    def _top20():
        n, l = int(.5 + length / 2.0), length
        yield "".join(str(i+1)[-1] for i in range(l))
        yield "1" * l
        yield "0" * l
        yield ("12" * n)[:l]
        yield "7" * l
        yield ("1" + max(0, l-2) * "0" + "4")[:l]
        yield "2" + max(0, l-1) * "0"
        yield "4" * l
        yield "2" * l
        yield ("69" * n)[:l]
        yield "9" * l
        yield "3" * l
        yield "5" * l
        yield "6" * l
        yield ("1" * n + "2" * n)[:l]
        yield ("13" * n)[:l]
        yield "8" * l
        yield "".join(str(i+1)[-1] for i in range(l))[::-1]
        yield ("2" + max(0, l-2) * "0" + "1")[:l]
        yield ("10" * n)[:l]
    
    done = []
    for code in _top20():
        if code in done:
            continue
        done.append(code)
        yield code
    # if length is 4, consider year-like PIN codes first
    if length == 4:
        for prefix in ["19", "20"]:
            for suffix in bruteforce(2, [digits, digits[::-1]][prefix == "19"], minlen=2):
                code = prefix + suffix
                if code not in done:
                    yield code
    for code in bruteforce(length, digits, minlen=length):
        if code in done:
            continue
        if length != 4 or not any(code.startswith(p) for p in ["19", "20"]):
            yield code


def bruteforce_re(regex):
    """ Generator for bruteforcing according to a given regular expression.
    
    Important note: due to the way the regex is handled, memory consumption can be really cumbersome with this function,
                     e.g. consider regex r"[a-c]{1,3}" ; in order to generate from 1 to 3 chars, it is necessary to
                           generate a single list with all possibilities of 1 to 3 chars (39 elements), to be put in the
                           product(...) for generating the output
                          so, if a larger alphabet and a greater upper limit are used, it can be very heavy for the
                           memory ; e.g. r"[a-zA-Z0-9]{1,8}" would generate >200T occurrences, which is of course
                           unsustainable for the memory
    
    :param regex: regular expression
    """
    if not is_str(regex):
        raise ValueError("Bad regex ; should be a string")
    for c in re.strings(regex):
        yield c if isinstance(c[0], int) else ''.join(c)


def dictionary(path, filter=None, rules=""):
    """ Generator for advanced dictionary attack handling a filter function and a set of rules.
    
    :param path:   path to the dictionary file
    :param filter: filter function
    :param rules:  rules to compute additional attempts
    """
    for rule in rules.split(","):
        list(parse_rule(rule))
    with open(path, 'rb') as f:
        for l in f:
            attempt = ensure_str(l.strip())
            if filter is None or filter(attempt):
                if rules:
                    for rule in rules.split(","):
                        tmp = attempt
                        for r in parse_rule(rule):
                            tmp = r(tmp)
                        yield tmp
                else:
                    yield attempt


def expand_mask(mask, charsets=None):
    """ Function for applying string expansion based on the following formats:       ?.              ?(...)
                                                                                      ^                 ^
                                                                                single group     multiple groups
    :param mask:     bruteforce mask
    :param charsets: custom alphabets for use with the mask
    """
    mask = ensure_str(mask)
    iterables, tmp_chars, charset, group = [], "", False, False
    masks = {k: v for k, v in MASKS.items()}
    masks.update(charsets or {})
    for i, c in enumerate(mask):
        if charset:
            if c == "?" and len(tmp_chars) == 0 and not group:
                charset = False
                iterables.append(c)
            elif c == "(":
                if len(tmp_chars) == 0 and not group:
                    group = True
                else:
                    raise ValueError("Bad mask ; unbalanced parenthesis in group starting at position {}".format(k))
            elif c == ")":
                if len(tmp_chars) > 0:
                    iterables.append(tmp_chars)
                    charset = False
                else:
                    raise ValueError("Bad mask ; empty group at position {}".format(k))
            elif group:
                try:
                    tmp_chars += masks[c]
                except KeyError:
                    tmp_chars += c
            else:
                try:
                    iterables.append(masks[c])
                except KeyError:
                    raise ValueError("Bad mask ; non-existing group '{}' at position {}".format(c, k))
                charset = False
            continue
        if c == "?":
            charset = True
            k = i
            continue
        iterables.append(c)
    if charset:
        raise ValueError("Bad mask ; unbalanced parenthesis in group starting at position {}".format(k))
    return iterables


def parse_rule(rule):
    """ Dictionary attack rule parsing function. """
    i = 0
    while i < len(rule):
        if i < len(rule) - 3 and rule[i+1] == "[":
            r = rule[i] + "[]"
            if r not in RULES.keys():
                raise ValueError("Bad rule ; '{}' does not exist".format(r))
            m = re.match(r".\[([^\[\]]*?)\]", rule[i:])
            if m is None:
                raise ValueError("Bad rule ; unbalanced bracket")
            t = m.group(1)
            yield RULES[r](t)
            i += len(m.group())
        else:
            r = rule[i]
            if r not in RULES.keys():
                raise ValueError("Bad rule ; '{}' does not exist".format(r))
            yield RULES[r]
            i += 1

