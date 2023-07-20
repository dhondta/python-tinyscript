#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Custom type validations' tests.

"""
import netaddr
import netifaces
from tinyscript.helpers.data.types import *

from utils import *


class TestHelpersDataTypes(TestCase):
    def setUp(self):
        global CFNAME, TF, TFNE
        CFNAME = ".test-data-types-config."
        TF   = "test_folder"
        TFNE = "test_folder_not_existing"
    
    @classmethod
    def tearDownClass(cls):
        for f in [TF, TFNE]:
            rmtree(f)
        for f in ["test1.txt", "test2.txt"]:
            remove(f)
        for ext in ["ini", "json", "toml", "yaml"]:
            remove(CFNAME + ext)
    
    def test_file_related_types(self):
        l1 = ["test1.txt", "test2.txt"]
        l2 = ["test1.txt", "test3.txt"]
        l3 = ["test3.txt", "test4.txt"]
        touch("test1.txt")
        with open("test2.txt", 'wt') as f:
            f.write("test")
        self.assertEqual(folder_does_not_exist(TF), TF)
        self.assertEqual(folder_exists_or_create(TF), TF)
        self.assertEqual(file_exists(l1[0]), l1[0])
        self.assertRaises(ValueError, file_does_not_exist, l1[0])
        self.assertRaises(ValueError, file_exists, l3[0])
        self.assertRaises(ValueError, file_exists, TF)
        self.assertEqual(file_mimetype("empty")(l1[0]), l1[0])
        self.assertRaises(ValueError, file_mimetype("text/plain"), l1[0])
        self.assertEqual(file_type("empty")(l1[0]), l1[0])
        self.assertRaises(ValueError, file_type("ASCII text"), l1[0])
        self.assertEqual(file_mimetype("text/plain")(l1[1]), l1[1])
        self.assertEqual(file_type("ASCII text")(l1[1]), l1[1])
        self.assertEqual(files_list(l1), l1)
        self.assertRaises(ValueError, files_list, l2)
        self.assertEqual(files_filtered_list(l2), [l2[0]])
        self.assertRaises(ValueError, files_filtered_list, l3)
        self.assertEqual(files_type("empty")([l1[0]]), [l1[0]])
        self.assertRaises(ValueError, files_type("empty"), l1)
        self.assertEqual(folder_exists(TF), TF)
        self.assertRaises(ValueError, folder_does_not_exist, TF)
        self.assertRaises(ValueError, folder_exists, TFNE)
        self.assertRaises(ValueError, folder_exists, l1[0])
        self.assertEqual(folder_exists_or_create(TFNE), TFNE)
        self.assertRaises(ValueError, folder_exists_or_create, l1[0])
        self.assertEqual(folder_exists(TFNE), TFNE)
        self.assertEqual(file_mode("750"), 488)
        self.assertEqual(file_mode("666"), 438)

    def test_general_purpose_types(self):
        self.assertEqual(int_range(1, 2), 1)
        self.assertEqual(int_range(2, 1, 5), 2)
        self.assertRaises(ValueError, int_range, 5, 3)
        self.assertRaises(ValueError, int_range, 5, 1, 3)
        self.assertEqual(neg_int(-1), -1)
        self.assertEqual(negative_int(-1), -1)
        self.assertRaises(ValueError, neg_int, 0)
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
        self.assertEqual(ints_range("1,2", 5), [1, 2])
        self.assertEqual(ints_range("[1,-1]", -2, 2), [1, -1])
        self.assertEqual(ints_range([1, 3, 2, 1], 5), [1, 3, 2, 1])
        self.assertRaises(ValueError, ints_range, "1,3", 2)
        self.assertRaises(ValueError, ints_range, "0,1", 1, 2)
        self.assertRaises(ValueError, ints_range, "0,1]", 1, 2)
        self.assertRaises(ValueError, ints_range, ["a", 1], 1, 2)
        self.assertEqual(neg_ints("-1"), [-1])
        self.assertEqual(negative_ints("[-1,-2]"), [-1, -2])
        self.assertRaises(ValueError, neg_ints, "-1,-2]")
        self.assertRaises(ValueError, neg_ints, [-1, 1])
        self.assertRaises(ValueError, neg_ints, "-1,0")
        self.assertRaises(ValueError, neg_ints, "test,0")
        self.assertEqual(pos_ints("1"), [1])
        self.assertEqual(positive_ints("[1,2]"), [1, 2])
        self.assertRaises(ValueError, pos_ints, "[1,2")
        self.assertRaises(ValueError, pos_ints, [-1, 1])
        self.assertRaises(ValueError, pos_ints, "test,0")
        self.assertEqual(str_matches(r"^[abc]$")("a"), "a")
        self.assertRaises(ValueError, str_matches(r"^[abc]$"), "d")
        self.assertEqual(str_contains("ABCD")("ADDCBABB"), "ADDCBABB")
        self.assertRaises(ValueError, str_contains, "ABCD", -.1)
        self.assertRaises(ValueError, str_contains, "ABCD", 1.1)
        self.assertEqual(regular_expression(r"^[abc]$"), r"^[abc]$")
        self.assertRaises(ValueError, regular_expression, r"^[abc")
        for i in ["a", 2.2, 10, 145, 1537]:
            self.assertRaises(ValueError, prime_number, i)
        for i in [2.0, 3, 5, 7, 11.0, 113]:
            self.assertEqual(prime_number(i), i)
        for il, ol in [("a,b,c", ["a","b","c"]), ("[1,2,3]", [1,2,3]), ("(a,b)", ["a","b"]), ("(a,", ["(a",""]),
                       ("1,2]", [1,"2]"]), (1, [1])]:
            self.assertEqual(values_list(il), ol)
            # note: ({"a"}, [{"a"}]) will fail in Python2 as ast.literal_eval will not be able to parse "set(['a'])",
            #        the representation of {"a"} (while in Python3, it succeeds)
    
    def test_config_related_types(self):
        INI    = '[section1]\ntest = "data"\nbool = true\n\n[section2]\ntest = "data"'
        JSON   = '{"test":"data"}'
        TOML   = 'title="test"\n\n[section1]\nfield = "data"\nbool = true\n\n[section2]\ntest = "data"'
        YAML   = "test:\n  - data: test\ntest2:\n  data: test"
        self.assertRaises(ValueError, ini_file, "does_not_exist")
        #self.assertTrue(is_ini(INI))  # FIXME: this test fails on Travis CI
        self.assertFalse(is_ini_file("does_not_exist"))
        cfg = CFNAME + "ini"
        with open(cfg, 'wt') as f:
            f.write(INI)
        self.assertIsNotNone(ini_file(cfg))
        self.assertRaises(ValueError, json_file, "does_not_exist")
        self.assertTrue(is_json(JSON))
        self.assertFalse(is_json_file("does_not_exist"))
        cfg = CFNAME + "json"
        with open(cfg, 'wt') as f:
            f.write(JSON)
        self.assertIsNotNone(json_file(cfg))
        self.assertRaises(ValueError, toml_file, "does_not_exist")
        self.assertTrue(is_toml(TOML))
        self.assertFalse(is_toml_file("does_not_exist"))
        cfg = CFNAME + "toml"
        with open(cfg, 'wt') as f:
            f.write(TOML)
        self.assertIsNotNone(toml_file(cfg))
        self.assertRaises(ValueError, yaml_file, "does_not_exist")
        self.assertTrue(is_yaml(YAML))
        self.assertFalse(is_yaml_file("does_not_exist"))
        cfg = CFNAME + "yaml"
        with open(cfg, 'wt') as f:
            f.write(YAML)
        self.assertIsNotNone(yaml_file(cfg))
    
    def test_hash_related_types(self):
        self.assertIsNotNone(any_hash("0" * 32))
        self.assertRaises(ValueError, any_hash, "bad_hash")
        self.assertRaises(ValueError, md5_hash, "bad_hash")
        self.assertRaises(ValueError, sha1_hash, "bad_hash")
        self.assertRaises(ValueError, sha224_hash, "bad_hash")
        self.assertRaises(ValueError, sha256_hash, "bad_hash")
        self.assertRaises(ValueError, sha512_hash, "bad_hash")
    
    def test_network_related_types(self):
        self.assertIsNotNone(domain_name("example.com"))
        self.assertIsNotNone(hostname("www.example.com"))
        self.assertRaises(ValueError, domain_name, "bad_name")
        self.assertRaises(ValueError, hostname, "www.example-.com")
        self.assertIsNotNone(url("http://www.example.com"))
        self.assertIsNotNone(url("http://john:doe@www.example.com/path?p=true"))
        self.assertRaises(ValueError, url, "bad_url")
        self.assertRaises(ValueError, url, "A" * 2050)
        self.assertRaises(ValueError, url, "A" * 40 + "://example.com")
        self.assertRaises(ValueError, url, "http://www.example-.com/")
        self.assertRaises(ValueError, url, "http://:@www.example.com/")
        self.assertIsNotNone(email_address("john.doe@www.example.com"))
        self.assertRaises(ValueError, email_address, "bad_email")
        self.assertRaises(ValueError, email_address, "user@bad_name")
        self.assertIsInstance(ip_address("127.0.0.1"), netaddr.IPAddress)
        self.assertIsInstance(ip_address("12345"), netaddr.IPAddress)
        self.assertIsInstance(ip_address("12345678900"), netaddr.IPAddress)
        self.assertRaises(ValueError, ipv4_address, "12345678900")
        self.assertIsInstance(ip_address("fe00::"), netaddr.IPAddress)
        self.assertRaises(ValueError, ip_address, "0.0.0.300")
        self.assertRaises(ValueError, ipv4_address, "0.0.0.300")
        self.assertRaises(ValueError, ip_address, "fe00:::")
        self.assertRaises(ValueError, ipv6_address, "fe00:::")
        self.assertIsInstance(list(ip_address_list("192.168.1.0/30")), list)
        self.assertRaises(ValueError, ip_address_list, "192.168.1.0.0/24")
        self.assertIsInstance(list(ip_address_network("192.168.1.0/30")), list)
        self.assertRaises(ValueError, ip_address_network, "192.168.1.0.0/24")
        self.assertIsInstance(mac_address(12345), netaddr.EUI)
        self.assertIsInstance(mac_address("01:02:03:04:05:06"), netaddr.EUI)
        self.assertRaises(ValueError, mac_address, "01:02:03-04:05:06")
        self.assertIsInstance(port_number(100), int)
        self.assertRaises(ValueError, port_number, -1)
        self.assertRaises(ValueError, port_number, 123456789)
        self.assertIsInstance(port_number_range(100), int)
        self.assertIsInstance(port_number_range("20-40"), list)
        self.assertRaises(ValueError, port_number_range, -1)
        self.assertRaises(ValueError, port_number_range, 123456789)
        self.assertRaises(ValueError, port_number_range, "40-20")
        GOOD = netifaces.interfaces()[0]
        BAD  = "THIS_INTERFACE_DOES_NOT_EXIST"
        self.assertTrue(network_interface(GOOD))
        self.assertRaises(ValueError, network_interface, BAD)
        AGOOD = list(netifaces.ifaddresses(GOOD).values())[0][0]['addr']
        ABAD  = "THIS_ADDRESS_IS_NOT_VALID"
        self.assertTrue(interface_address(AGOOD))
        self.assertRaises(ValueError, interface_address, BAD)
        self.assertTrue(interface_address_list([AGOOD]))
        self.assertRaises(ValueError, interface_address_list, [BAD])
        self.assertEqual(interface_address_filtered_list([BAD]), [])
        GGOOD = list(netifaces.gateways()['default'].values())
        if len(GGOOD) > 0:
            self.assertTrue(gateway_address(GGOOD[0][0]))
            self.assertTrue(default_gateway_address(GGOOD[0][0]))
        GBAD  = "THIS_GATEWAY_ADDRESS_IS_NOT_VALID"
        self.assertRaises(ValueError, gateway_address, GBAD)
        self.assertRaises(ValueError, default_gateway_address, GBAD)
        ASN1 = 12345
        ASN2 = "4835354"
        ASN3 = "BAD_ASN"
        self.assertTrue(as_number(ASN1))
        self.assertTrue(as_number(ASN2))
        self.assertRaises(ValueError, as_number, ASN3)

    def test_data_type_check(self):
        self.assertTrue(is_int(1))
        self.assertFalse(is_int("a"))
        self.assertTrue(is_int_range(1, 1, 2))
        self.assertFalse(is_int_range(0, 1, 2))
        self.assertFalse(is_int_range("a", 1, 2))
        self.assertTrue(is_percentage(0))
        self.assertTrue(is_percentage(1))
        self.assertFalse(is_percentage(2))
        self.assertTrue(is_percentage(.1))
        self.assertFalse(is_percentage(".123"))
        self.assertTrue(is_pos_int(10))
        self.assertTrue(is_pos_int(0, True))
        self.assertFalse(is_pos_int(0, False))
        self.assertFalse(is_pos_int(-10))
        self.assertTrue(is_neg_int(-10))
        self.assertFalse(is_neg_int(10))
        for i in ["a", 2.2, 10, 145, 1537]:
            self.assertFalse(is_prime(i))
        for i in [2.0, 3, 5, 7, 11.0, 113]:
            self.assertTrue(is_prime(i))
        self.assertTrue(is_dict({"key": "value"}))
        self.assertFalse(is_dict("not_a_dict"))
        self.assertFalse(is_dict(["not_a_dict"]))
        self.assertTrue(is_list([0]))
        self.assertTrue(is_list((0, )))
        self.assertTrue(is_list({0}))
        self.assertFalse(is_list("not_a_list"))
        self.assertTrue(is_str("test"))
        self.assertFalse(is_str(1))
        self.assertTrue(is_lowercase("test"))
        self.assertTrue(is_uppercase("TEST"))
        self.assertTrue(is_printable("test1234!"))
        self.assertFalse(is_lowercase("Test"))
        self.assertTrue(is_lowercase("Test", .75))
        self.assertTrue(is_regex("test(ok)"))
        self.assertFalse(is_regex("test("))
        self.assertTrue(is_lambda(dummy_lambda))
        self.assertFalse(is_lambda(True))
        self.assertTrue(is_function(dummy_lambda))
        self.assertTrue(is_function(dummy_function))
        self.assertFalse(is_function("not_a_function"))
        self.assertTrue(is_module(netaddr))
        self.assertFalse(is_module(dummy_function))
        self.assertFalse(is_module("not_a_module"))
    
    def test_data_format_check(self):
        self.assertTrue(is_bin("01000111"))
        self.assertFalse(is_bin("0123"))
        self.assertTrue(is_hex("deadbeef"))
        self.assertTrue(is_hex("c0ffee"))
        self.assertFalse(is_hex("coffee"))
        self.assertFalse(is_hex("00a"))
        self.assertTrue(is_md5("0" * 32))
        self.assertTrue(is_hash("0" * 32))
        self.assertTrue(is_sha1("a" * 40))
        self.assertTrue(is_sha224("1" * 56))
        self.assertTrue(is_sha256("b" * 64))
        self.assertTrue(is_sha512("2" * 128))
        self.assertTrue(is_hash("0" * 128))
        self.assertFalse(is_hash("not_a_hash"))
    
    def test_network_format_check(self):
        self.assertTrue(is_domain("example.com"))
        self.assertTrue(is_hostname("www.example.com"))
        self.assertTrue(is_url("http://www.example.com"))
        self.assertTrue(is_url("http://john:doe@www.example.com/path?p=true"))
        self.assertFalse(is_url("http:/example.com"))
        self.assertFalse(is_url("http://www.example-.com/"))
        self.assertFalse(is_url("A" * 40 + "://example.com"))
        self.assertFalse(is_url("http://:@www.example.com/"))
        self.assertFalse(is_email("example.com"))
        self.assertTrue(is_email("test@example.com"))
        self.assertTrue(is_ip("1234"))
        self.assertTrue(is_ipv4("1234"))
        self.assertTrue(is_ipv6("12345678900"))
        self.assertFalse(is_ipv4("12345678900"))
        self.assertFalse(is_ipv6("1234567890123456789012345678901234567890123"))
        self.assertTrue(is_ipv6("123456789012345678901234567890123456789"))
        self.assertTrue(is_ip("127.0.0.1"))
        self.assertTrue(is_ipv4("127.0.0.1"))
        self.assertTrue(is_ip("fe00::"))
        self.assertTrue(is_ipv6("fe00::"))
        self.assertTrue(is_ipnet("192.168.1.0/24"))
        self.assertTrue(is_ipv4net("192.168.1.0/24"))
        self.assertTrue(is_ipnet("fe00::/24"))
        self.assertTrue(is_ipv6net("fe00::/24"))
        self.assertFalse(is_ipnet("abc"))
        self.assertFalse(is_ipv4net("abc"))
        self.assertFalse(is_ipv6net("abc"))
        self.assertTrue(is_ipv6net("dead::babe"))
        self.assertFalse(is_ipv6net("dead:babe"))
        GOOD = ["1.2.3.4", "fe00::", "127.0.0.0/30"]
        BAD1 = ["1.2.3.300", "fe00::", "127.0.0.0/30"]
        BAD2 = ["1.2.3.4", "fe00::", "127.0.0.0/40"]
        self.assertTrue(all(is_ip(_) for _ in ip_address_list(GOOD)))
        self.assertRaises(ValueError, ip_address_list, BAD1)
        self.assertRaises(ValueError, ip_address_list, BAD2)
        self.assertRaises(ValueError, ipv4_address_list, BAD1)
        self.assertRaises(ValueError, ipv6_address_list, BAD2)
        self.assertTrue(all(is_ip(_) for _ in ip_address_filtered_list(BAD1)))
        self.assertTrue(all(is_ip(_) for _ in ip_address_filtered_list(BAD2)))
        self.assertTrue(all(is_ip(_) for _ in ipv4_address_filtered_list(BAD1)))
        self.assertTrue(all(is_ip(_) for _ in ipv6_address_filtered_list(BAD2)))
        self.assertTrue(is_mac("12345"))
        self.assertTrue(is_mac("01:02:03:04:05:06"))
        self.assertTrue(is_mac("01-02-03-04-05-06"))
        self.assertFalse(is_mac("01:02:03:04:05"))
        self.assertFalse(is_mac("01|02|03|04|05|06"))
        GOOD = netifaces.interfaces()[0]
        BAD  = "THIS_INTERFACE_DOES_NOT_EXIST"
        self.assertTrue(is_netif(GOOD))
        self.assertFalse(is_netif(BAD))
        AGOOD = list(netifaces.ifaddresses(GOOD).values())[0][0]['addr']
        ABAD  = "THIS_ADDRESS_IS_NOT_VALID"
        self.assertTrue(is_ifaddr(AGOOD))
        self.assertFalse(is_ifaddr(ABAD))
        GBAD  = "THIS_GATEWAY_ADDRESS_IS_NOT_VALID"
        self.assertFalse(is_gw(GBAD))
        self.assertFalse(is_defgw(GBAD))
        ASN1 = 12345
        ASN2 = "BAD_ASN"
        self.assertTrue(is_asn(ASN1))
        self.assertFalse(is_asn(ASN2))

    def test_option_format_check(self):
        self.assertTrue(is_long_opt("--test"))
        self.assertFalse(is_long_opt("-t"))
        self.assertTrue(is_short_opt("-t"))
        self.assertFalse(is_short_opt("--test"))

