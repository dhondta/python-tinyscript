#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common custom type validations' tests.

"""
import ipaddress
from unittest import main, TestCase

from tinyscript.helpers.types import *

from utils import *


class TestHelpersTypes(TestCase):
    def test_general_purpose_types(self):
        tf = "test_folder"
        tfne = "test_folder_not_existing"
        l1 = ["test1.txt", "test2.txt"]
        l2 = ["test1.txt", "test3.txt"]
        l3 = ["test3.txt", "test4.txt"]
        touch("test1.txt", "test2.txt")
        makedirs(tf)
        self.assertEqual(file_exists(l1[0]), l1[0])
        self.assertRaises(ValueError, file_exists, l3[0])
        self.assertRaises(ValueError, file_exists, tf)
        self.assertEqual(files_list(l1), l1)
        self.assertRaises(ValueError, files_list, l2)
        self.assertEqual(files_filtered_list(l2), [l2[0]])
        self.assertRaises(ValueError, files_filtered_list, l3)
        self.assertEqual(folder_exists(tf), tf)
        self.assertRaises(ValueError, folder_exists, tfne)
        self.assertRaises(ValueError, folder_exists, l1[0])
        rmdir(tf)
        self.assertEqual(folder_exists_or_create(tfne), tfne)
        self.assertRaises(ValueError, folder_exists_or_create, l1[0])
        self.assertEqual(folder_exists(tfne), tfne)
        rmdir(tfne)
        remove("test1.txt")
        remove("test2.txt")
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
        self.assertEqual(ints("1,-1"), [1, -1])
        self.assertEqual(ints("[1,-1]"), [1, -1])
        self.assertRaises(ValueError, ints, "0,1]")
        self.assertRaises(ValueError, ints, ["a", 1])
        self.assertEqual(neg_ints("-1"), [-1])
        self.assertEqual(negative_ints("[0,-2]"), [0, -2])
        self.assertRaises(ValueError, neg_ints, "0,-2]")
        self.assertRaises(ValueError, neg_ints, [-1, 1])
        self.assertRaises(ValueError, neg_ints, "test,0")
        self.assertEqual(pos_ints("1"), [1])
        self.assertEqual(positive_ints("[1,2]"), [1, 2])
        self.assertRaises(ValueError, pos_ints, "[1,2")
        self.assertRaises(ValueError, pos_ints, [-1, 1])
        self.assertRaises(ValueError, pos_ints, "test,0")
        

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
