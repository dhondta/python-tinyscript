#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common custom type checking and validation functions.

"""
import ipaddress
import re
from os import makedirs
from os.path import exists, isdir, isfile
from six import string_types, u

from ..__info__ import __author__, __copyright__, __version__


__all__ = __features__ = [
    "file_exists", "files_list", "files_filtered_list", 
    "folder_exists", "folder_exists_or_create",
    "neg_int", "negative_int", "pos_int", "positive_int", "ints", "neg_ints",
        "negative_ints", "pos_ints", "positive_ints",
    "ip_address", "ip_address_list", "ip_address_network", "port_number",
        "port_number_range"
]


# -------------------- TYPE/FORMAT CHECKING FUNCTIONS --------------------
# various object type check functions
__all__ += ["is_dict", "is_function", "is_int", "is_lambda", "is_list",
            "is_neg_int", "is_pos_int", "is_str"]
is_int      = lambda i: isinstance(i, int)
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
is_bin = lambda b, sep=None: is_str(b) and \
                             all(c in "01" + (sep or "") for c in set(b))
is_hex = lambda h: is_str(h) and len(h) % 2 == 0 and \
                   all(c in "0123456789abcdef" for c in set(h.lower()))

# some other common check function
__all__ += ["is_long_opt", "is_short_opt"]
is_long_opt  = lambda o: is_str(o) and len(o) > 2 and o.startswith('--')
is_short_opt = lambda o: is_str(o) and len(o) == 2 and o.startswith('-')


# -------------------- GENERAL-PURPOSE TYPES --------------------
def __str2list(l):
    """ Convert string to list if input is effectively a string. """
    if isinstance(l, string_types):
        if l[0] == '[' and l[-1] == ']':
            l = l[1:-1]
        l = list(map(lambda x: x.strip(), l.split(',')))
    return l


def file_exists(f):
    """ Check that the given file exists. """
    if not exists(f):
        raise ValueError("File does not exist")
    if not isfile(f):
        raise ValueError("Target exists and is not a file")
    return f


def files_list(l, filter_bad=False):
    """ Check if the list contains valid files. """
    l = __str2list(l)
    nl = []
    for f in l:
        if not isfile(f):
            if not filter_bad:
                raise ValueError("A file from the given list does not exist")
        else:
            nl.append(f)
    if filter_bad and len(nl) == 0:
        raise ValueError("No valid file in the given list")
    return nl


def files_filtered_list(l):
    """ Check if the list contains valid files and discard invalid ones. """
    return files_list(l, True)


def folder_exists(f):
    """ Check that the given folder exists. """
    if not exists(f):
        raise ValueError("Folder does not exist")
    if not isdir(f):
        raise ValueError("Target exists and is not a folder")
    return f


def folder_exists_or_create(f):
    """ Check that the given folder exists and create it if not existing. """
    if not exists(f):
        makedirs(f)
    if not isdir(f):
        raise ValueError("Target exists and is not a folder")
    return f


def ints(l, ifilter=lambda x: x, idescr=None):
    """ Parses a comma-separated list of ints. """
    l = __str2list(l)
    try:
        l = list(map(ifilter, list(map(int, l))))
    except:
        raise ValueError("Bad list of {}integers"
                         .format("" if idescr is None else idescr + " "))
    return l
negative_ints = neg_ints = lambda l: ints(l, neg_int, "negative")
positive_ints = pos_ints = lambda l: ints(l, pos_int, "positive")


def neg_int(i):
    """ Simple negative integer validation. """
    try:
        if isinstance(i, string_types):
            i = int(i)
        if not isinstance(i, int) or i > 0:
            raise Exception()
    except:
        raise ValueError("Not a negative integer")
    return i
negative_int = neg_int


def pos_int(i):
    """ Simple positive integer validation. """
    try:
        if isinstance(i, string_types):
            i = int(i)
        if not isinstance(i, int) or i < 0:
            raise Exception()
    except:
        raise ValueError("Not a positive integer")
    return i
positive_int = pos_int


# -------------------- NETWORK-RELATED TYPES --------------------
def ip_address(ip):
    """ IP address validation. """
    # note: ipaddress already handles validation and raises a ValueError in case
    #        of bad address ; we just ensure that the input is converted to
    #        unicode using six.u (otherwise, it fails in Python 2)
    return ipaddress.ip_address(u(ip))


def ip_address_list(ips):
    """ IP address range validation and expansion. """
    # first, try it as a single IP address
    try:
        return ip_address(ips)
    except ValueError:
        pass
    # then, consider it as an ipaddress.IPv[4|6]Network instance and expand it
    return list(ipaddress.ip_network(u(ips)).hosts())


def ip_address_network(inet):
    """ IP address network validation. """
    # first, try it as a normal IP address
    try:
        return ip_address(inet)
    except ValueError:
        pass
    # then, consider it as an ipaddress.IPv[4|6]Network instance
    return ipaddress.ip_network(u(inet))


def port_number(port):
    """ Port number validation. """
    try:
        port = int(port)
    except ValueError:
        raise ValueError("Bad port number")
    if not 0 <= port < 2 ** 16:
        raise ValueError("Bad port number")
    return port


def port_number_range(prange):
    """ Port number range validation and expansion. """
    # first, try it as a normal port number
    try:
        return port_number(prange)
    except ValueError:
        pass
    # then, consider it as a range with the format "x-y" and expand it
    try:
        bounds = list(map(int, re.match(r'^(\d+)\-(\d+)$', prange).groups()))
        if bounds[0] > bounds[1]:
            raise AttributeError()
    except (AttributeError, TypeError):
        raise ValueError("Bad port number range")
    return list(range(bounds[0], bounds[1] + 1))
