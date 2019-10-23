#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common custom type checking and validation functions.

"""
import ast
import netaddr
import netifaces
import re
from itertools import chain
from os import makedirs
from os.path import exists, isdir, isfile
from six import string_types, u

from ..__info__ import __author__, __copyright__, __version__


__all__ = __features__ = []

try:
    long
except NameError:
    long = int


# -------------------- TYPE/FORMAT CHECKING FUNCTIONS --------------------
# various object type check functions
__all__ += ["is_dict", "is_function", "is_int", "is_lambda", "is_list",
            "is_neg_int", "is_pos_int", "is_str"]
is_int      = lambda i: isinstance(i, (int, long))
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
is_bin = lambda b: is_str(b) and all(set(_).difference(set("01")) == set() \
                                     for _ in re.split(r"\W+", b))
is_hex = lambda h: is_str(h) and len(h) % 2 == 0 and \
                   set(h.lower()).difference(set("0123456789abcdef")) == set()

# some other common check functions
__all__ += ["is_long_opt", "is_short_opt"]
is_long_opt  = lambda o: is_str(o) and \
                         re.match(r"^--[a-z]+(-[a-z]+)*$", o, re.I)
is_short_opt = lambda o: is_str(o) and re.match(r"^-[a-z]$", o, re.I)

# some network-related check functions
__all__ += ["is_defgw", "is_gw", "is_ifaddr", "is_ip", "is_ipv4", "is_ipv6",
            "is_mac", "is_netif", "is_port"]
is_defgw  = lambda gw:  __gateway_address(gw, True, False) is not None
is_gw     = lambda gw:  __gateway_address(gw, False, False) is not None
is_ifaddr = lambda ip:  __interface_address(ip, False) is not None
is_ip     = lambda ip:  __ip_address(ip, None, False) is not None
is_ipv4   = lambda ip:  __ip_address(ip, 4, False) is not None
is_ipv6   = lambda ip:  __ip_address(ip, 6, False) is not None
is_mac    = lambda mac: __mac_address(mac, False) is not None
is_netif  = lambda nif: __network_interface(nif, False) is not None
is_port   = lambda p:   is_int(p) and 0 < p < 2**16

# dummy shortcuts, compliant with the is_* naming convention
__all__ += ["is_dir", "is_file", "is_folder"]
is_dir = is_folder = isdir
is_file = isfile


def __str2list(s):
    """ Convert string to list if input is effectively a string. """
    # if already a list, simply return it, otherwise ensure input is a string
    if isinstance(s, list):
        return s
    else:
        s = str(s)
    # remove heading and trailing brackets
    if s[0] == '[' and s[-1] == ']' or s[0] == '(' and s[-1] == ')':
        s = s[1:-1]
    # then parse list elements from the string
    l = []
    for i in s.split(","):
        i = i.strip()
        try:
            l.append(ast.literal_eval(i))
        except Exception:
            l.append(i)
    return l


# -------------------- FILE/FOLDER-RELATED ARGUMENT TYPES --------------------
__all__ += ["file_exists", "files_list", "files_filtered_list", "folder_exists",
            "folder_exists_or_create"]


def file_exists(f):
    """ Check that the given file exists. """
    if not exists(f):
        raise ValueError("'{}' does not exist".format(f))
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
        raise ValueError("'{}' does not exist".format(f))
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


# -------------------- DATA FORMAT ARGUMENT TYPES --------------------
__all__ += ["neg_int", "negative_int", "pos_int", "positive_int", "ints",
            "neg_ints", "negative_ints", "pos_ints", "positive_ints"]


def __ints(l, check_func=lambda x: False, idescr=None, **kwargs):
    """ Parses a comma-separated list of ints. """
    l = __str2list(l)
    msg = "{} {}integer{}".format(["Bad list of", "Not a"][len(l) == 1],
                                  "" if idescr is None else idescr + " ",
                                  ["s", ""][len(l) == 1])
    if not all(check_func(_, **kwargs) for _ in l):
        raise ValueError(msg)
    return l
ints = lambda l: __ints(l, is_int)
negative_int = neg_int = \
    lambda i, zero=False: __ints(i, is_neg_int, "negative", zero=zero)[0]
positive_int = pos_int = \
    lambda i, zero=True: __ints(i, is_pos_int, "positive", zero=zero)[0]
negative_ints = neg_ints = \
    lambda l, zero=False: __ints(l, is_neg_int, "negative", zero=zero)
positive_ints = pos_ints = \
    lambda l, zero=True: __ints(l, is_pos_int, "positive", zero=zero)


# -------------------- NETWORK-RELATED ARGUMENT TYPES --------------------
__all__ += ["default_gateway_address", "gateway_address", "ip_address",
            "ipv4_address", "ipv6_address", "ip_address_list",
            "ipv4_address_list", "ipv6_address_list",
            "ip_address_filtered_list", "ipv4_address_filtered_list",
            "ipv6_address_filtered_list", "ip_address_network",
            "ipv4_address_network", "ipv6_address_network",
            "interface_address", "interface_address_list",
            "interface_address_filtered_list", "mac_address",
            "network_interface", "port_number", "port_number_range"]


def __gateway_address(gw, default=False, fail=True):
    """ Gateway IP address validation. """
    g = netifaces.gateways() if not default else netifaces.gateways()['default']
    for k, v in g.items():
        if k == "default":
            continue
        if isinstance(v, tuple):
            v = [v]
        for l in v:
            if gw == l[0]:
                return gw
    if fail:
        raise ValueError("Bad {}gateway".format(["", "default "][default]))
default_gateway_address = lambda gw: __gateway_address(gw, True)
gateway_address = lambda gw: __gateway_address(gw)


def __interface_address(addr, fail=True):
    """ Interface address validation. """
    for iface in netifaces.interfaces():
        for k, v in netifaces.ifaddresses(iface).items():
            for d in v:
                if addr in d.values():
                    return addr
    if fail:
        raise ValueError("Bad interface address")
interface_address = lambda a: __interface_address(a)


def __interface_address_list(addrs, filter_bad=False):
    """ Interface addresses validation and expansion. """
    addrs = __str2list(addrs)
    l = []
    for addr in addrs:
        try:
            l.append(__interface_address(addr))
        except ValueError as e:
            if not filter_bad:
                raise ValueError(str(e))
    return l
interface_address_list          = lambda a: __interface_address_list(a)
interface_address_filtered_list = lambda a: __interface_address_list(a, True)


def __ip_address(ip, version=None, fail=True):
    """ IP address validation. """
    # note: netaddr already handles validation and raises a ValueError in case
    #        of bad address ; we just ensure that the input is converted to
    #        unicode using six.u (otherwise, it fails in Python 2)
    ip = int(ip) if str(ip).isdigit() else str(ip)
    try:
        return netaddr.IPAddress(ip, version=version)
    except (ValueError, netaddr.core.AddrFormatError) as e:
        if fail:
            raise ValueError(str(e))
ip_address = lambda ip: __ip_address(ip)
ipv4_address = lambda ip: __ip_address(ip, 4)
ipv6_address = lambda ip: __ip_address(ip, 6)


def __ip_address_list(ips, version=None, filter_bad=False):
    """ IP address range validation and expansion. """
    ips = __str2list(ips)
    # consider it as an ipaddress.IPv[4|6]Network instance and expand it
    l = []
    for ip in ips:
        # parse it as a single IP
        _ = __ip_address(ip, version, False)
        if _ is not None and _ not in l:
            l.append([_])
            continue
        # parse it as a network
        try:
            l.append(netaddr.IPNetwork(ip, version=version))
        except (ValueError, netaddr.core.AddrFormatError) as e:
            if not filter_bad:
                raise ValueError(str(e))
    # make a generator with the parsed IP addresses/networks
    def __generator():
        _ = []
        for ip in chain(*l):
            if ip not in _:
                yield str(ip)
                _.append(ip)
    if len(l) > 0:
        return __generator()
ip_address_list            = lambda ips: __ip_address_list(ips)
ip_address_filtered_list   = lambda ips: __ip_address_list(ips, None, True)
ipv4_address_list          = lambda ips: __ip_address_list(ips, 4)
ipv4_address_filtered_list = lambda ips: __ip_address_list(ips, 4, True)
ipv6_address_list          = lambda ips: __ip_address_list(ips, 6)()
ipv6_address_filtered_list = lambda ips: __ip_address_list(ips, 6, True)
ip_address_network         = lambda net: __ip_address_list([net], None)
ipv4_address_network       = lambda net: __ip_address_list([net], 4)
ipv6_address_network       = lambda net: __ip_address_list([net], 6)


def __mac_address(mac, fail=True):
    """ MAC address validation. """
    msg = "'{}' does not appear to be a MAC address".format(mac)
    # check as an integer
    if str(mac).isdigit():
        mac = int(mac)
    try:
        return netaddr.EUI(mac)
    except (ValueError, netaddr.core.AddrFormatError) as e:
        if fail:
            raise ValueError(str(e))
        else:
            return
mac_address = lambda mac: __mac_address(mac)


def __network_interface(netif, fail=True):
    """ Network interface validation. """
    if netif in netifaces.interfaces():
        return netif
    if fail:
        raise ValueError("Not an existing interface")
network_interface = lambda nif: __network_interface(nif)


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
