# -*- coding: UTF-8 -*-
"""Common utility functions.

"""
import re
from itertools import permutations, product
from string import printable, punctuation

from .compat import b, ensure_str
from .data import is_file, is_list, is_str


__all__ = __features__ = ["bruteforce", "bruteforce_mask", "dictionary", "expand_mask", "parse_rule"]


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
    """
    Generator for bruteforcing according to minimum and maximum lengths and an alphabet.
    
    :param maxlen:   maximum bruteforce entry length
    :param alphabet: bruteforce alphabet to be used
    :param minlen:   minimum bruteforce entry length (optional)
    :param repeat:   whether alphabet characters can be repeated or not
    :yield:          bruteforce entry
    """
    for i in range(minlen, maxlen + 1):
        if repeat:
            for c in product(alphabet, repeat=i):
                yield c if isinstance(c[0], int) else ''.join(c)
        else:
            for c in permutations(alphabet, i):
                yield c if isinstance(c[0], int) else ''.join(c)


def bruteforce_mask(mask, charsets=None):
    """
    Generator for bruteforcing according to a given mask (mostly similar to this used in hashcat).
    
    :param mask:     bruteforce mask
    :param charsets: custom alphabets for use with the mask
    """
    if is_str(mask):
        mask = expand_mask(mask, charsets)
    if not is_list(mask) or any(not is_str(x) for x in mask):
        raise ValueError("Bad mask ; should be a string or a list of strings, got {}".format(type(mask)))
    for c in product(*mask):
        yield c if isinstance(c[0], int) else ''.join(c)


def dictionary(path, filter=None, rules=""):
    """
    Generator for advanced dictionary attack handling a filter function and a set of rules.
    
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
    """
    Function for applying string expansion based on the following formats:       ?.              ?(...)
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
    """
    Dictionary attack rule parsing function.
    """
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
