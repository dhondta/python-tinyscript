#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common custom type validations.

"""
import ipaddress
import re
from six import u

from ..__info__ import __author__, __copyright__, __version__


__all__ = __features__ = ["neg_int", "negative_int", "pos_int", "positive_int",
                          "ip_address", "ip_address_list", "ip_address_network",
                          "port_number", "port_number_range"]


# -------------------- GENERAL-PURPOSE TYPES --------------------
def neg_int(i):
    """ Simple negative integer validation. """
    if not isinstance(i, int) or i > 0:
        raise ValueError("Not a negative integer")
    return i
negative_int = neg_int


def pos_int(i):
    """ Simple positive integer validation. """
    if not isinstance(i, int) or i < 0:
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
