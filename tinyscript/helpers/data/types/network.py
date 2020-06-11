# -*- coding: UTF-8 -*-
"""Network-related checking functions and argument types.

"""
import netaddr
import netifaces
import re
from email.utils import parseaddr as parse_email
from itertools import chain

from .strings import _str2list


__all__ = __features__ = []


# network-related check functions
__all__ += ["is_asn", "is_defgw", "is_domain", "is_email", "is_gw", "is_hostname", "is_ifaddr", "is_ip", "is_ipnet",
            "is_ipv4", "is_ipv4net", "is_ipv6", "is_ipv6net", "is_mac", "is_netif", "is_port", "is_url"]
is_asn      = lambda a:   __as_number(a, False) is not None
is_defgw    = lambda gw:  __gateway_address(gw, True, False) is not None
is_domain   = lambda n:   __domain_name(n, False, False) is not None
is_email    = lambda e:   __email_address(e, False) is not None
is_gw       = lambda gw:  __gateway_address(gw, False, False) is not None
is_hostname = lambda h:   __hostname(h, False) is not None
is_ifaddr   = lambda ip:  __interface_address(ip, False) is not None
is_ip       = lambda ip:  __ip_address(ip, None, False) is not None
is_ipnet    = lambda n:   __ip_address_list([n], None, fail=False) is not None
is_ipv4     = lambda ip:  __ip_address(ip, 4, False) is not None
is_ipv4net  = lambda n:   __ip_address_list([n], 4, fail=False) is not None
is_ipv6     = lambda ip:  __ip_address(ip, 6, False) is not None
is_ipv6net  = lambda n:   __ip_address_list([n], 6, fail=False) is not None
is_mac      = lambda mac: __mac_address(mac, False) is not None
is_netif    = lambda nif: __network_interface(nif, False) is not None
is_port     = lambda p:   isinstance(p, int) and 0 < p < 2**16
is_url      = lambda url: __url(url, False) is not None


# network-related argument types
__all__ += ["as_number", "default_gateway_address", "domain_name", "email_address", "gateway_address", "hostname",
            "ip_address", "ipv4_address", "ipv6_address", "ip_address_list", "ipv4_address_list", "ipv6_address_list",
            "ip_address_filtered_list", "ipv4_address_filtered_list", "ipv6_address_filtered_list",
            "ip_address_network", "ipv4_address_network", "ipv6_address_network", "interface_address",
            "interface_address_list", "interface_address_filtered_list", "mac_address", "network_interface",
            "port_number", "port_number_range", "url"]


def __as_number(asn, fail=True):
    """ Autonomous System Number validation. """
    if str(asn).isdigit() and 0 <= int(asn) < 2**32:
        return asn
    if fail:
        raise ValueError("Bad AS number")
as_number = lambda a: __as_number(a)


def __domain_name(name, dotted=False, fail=True):
    """ Domain name validation. """
    if not dotted and not name.endswith("."):
        name += "."
    # source: https://stackoverflow.com/questions/19705002/
    if len(name) <= 255 and re.match(r"^(((([a-z0-9]+){1,63}\.)|(([a-z0-9]+"
                r"(\-)+[a-z0-9]+){1,63}\.))+){1,255}$", name, re.I) is not None:
        return name
    if fail:
        raise ValueError("Bad domain name")
domain_name = lambda n: __domain_name(n)


def __email_address(email, fail=True):
    """ Email address validation. """
    # reference: https://stackoverflow.com/questions/8022530/
    if len(email) <= 320 and re.match(r"^[^@]+@[^@]+$", email) and \
       is_hostname(email.split("@")[1]) and parse_email(email)[1] != "":
        return email
    if fail:
        raise ValueError("Bad email address")
email_address = lambda e: __email_address(e)


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
gateway_address         = lambda gw: __gateway_address(gw)


HN = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.I)
def __hostname(hostname, fail=True):
    """ Hostname validation. """
    if len(hostname) <= 255 and all(HN.match(x) for x in \
       hostname.rstrip(".").split(".")):
        return hostname
    if fail:
        raise ValueError("Bad hostname")
hostname = lambda h: __hostname(h)


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
    addrs = _str2list(addrs)
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
ip_address   = lambda ip: __ip_address(ip)
ipv4_address = lambda ip: __ip_address(ip, 4)
ipv6_address = lambda ip: __ip_address(ip, 6)


def __ip_address_list(ips, version=None, filter_bad=False, fail=True):
    """ IP address range validation and expansion. """
    ips = _str2list(ips)
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
            if not filter_bad and fail:
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
ipv6_address_list          = lambda ips: __ip_address_list(ips, 6)
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


def __url(url, fail=True):
    """ URL hyperlink. """
    if len(url) > 2048:
        raise ValueError("Not a valid URL (too long)")
    try:
        scheme, link = url.split("://")
    except ValueError:
        if fail:
            raise ValueError("Not a valid URL (cannot parse scheme)")
        else:
            return
    if len(scheme) > 36:
        if fail:
            raise ValueError("Not a valid URL (invalid scheme)")
        else:
            return
    link = link.split("?")
    link, query = link if len(link) == 2 else (link[0], "")
    link = link.split("/")
    link, reqpath = link if len(link) == 2 else (link[0], "")
    link = link.split("@")
    auth, domain = link if len(link) == 2 else ("", link[0])
    if not is_domain(domain):
        if fail:
            raise ValueError("Not a valid URL (bad domain)")
        else:
            return
    auth = auth.split(":")
    if auth != [''] and (len(auth) != 2 or auth[0] == "" and auth[1] == ""):
        if fail:
            raise ValueError("Not a valid URL (bad auth)")
        else:
            return
    return url
url = lambda url: __url(url)


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

