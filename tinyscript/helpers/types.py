#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common custom type validations.

"""
import ipaddress
import re
from six import u

from ..__info__ import __author__, __copyright__, __version__


__all__ = __features__ = ["ip_address", "ip_address_list", "ip_address_network",
                          "port_number", "port_number_range"]


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
    if not (port.isdigit() and 0 <= int(port) < 2 ** 16):
        raise ValueError("Bad port number")
    return int(port)


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
    except AttributeError:
        raise ValueError("Bad port number range")
    return list(range(bounds[0], bounds[1] + 1))
