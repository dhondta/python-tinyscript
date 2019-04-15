#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common custom type validations' tests.

"""
import ipaddress
from unittest import main, TestCase

from tinyscript.helpers.types import *


class TestHelpersTypes(TestCase):
    def test_general_purpose_types(self):
        self.assertEqual(neg_int(0), 0)
        self.assertEqual(neg_int(-1), -1)
        self.assertEqual(negative_int(-1), -1)
        self.assertRaises(ValueError, neg_int, 1)
        self.assertRaises(ValueError, neg_int, -1.2)
        self.assertRaises(ValueError, neg_int, "test")
        self.assertEqual(pos_int(0), 0)
        self.assertEqual(pos_int(1), 1)
        self.assertEqual(positive_int(1), 1)
        self.assertRaises(ValueError, pos_int, -1)
        self.assertRaises(ValueError, pos_int, 1.2)
        self.assertRaises(ValueError, pos_int, "test")
        

    def test_network_related_types(self):
        self.assertIsInstance(ip_address("127.0.0.1"), ipaddress.IPv4Address)
        self.assertIsInstance(ip_address("fe00::"), ipaddress.IPv6Address)
        self.assertRaises(ValueError, ip_address, "0.0.0.300")
        self.assertRaises(ValueError, ip_address, "fe00:::")
        self.assertIsInstance(ip_address_list("192.168.1.0/24"), list)
        self.assertRaises(ValueError, ip_address_list, "192.168.1.0.0/24")
        self.assertIsInstance(ip_address_network("192.168.1.0/24"),
                              ipaddress.IPv4Network)
        self.assertRaises(ValueError, ip_address_network, "192.168.1.0.0/24")
        self.assertIsInstance(port_number(100), int)
        self.assertRaises(ValueError, port_number, -1)
        self.assertRaises(ValueError, port_number, 123456789)
        self.assertIsInstance(port_number_range(100), int)
        self.assertIsInstance(port_number_range("20-40"), list)
        self.assertRaises(ValueError, port_number_range, -1)
        self.assertRaises(ValueError, port_number_range, 123456789)
        self.assertRaises(ValueError, port_number_range, "40-20")
