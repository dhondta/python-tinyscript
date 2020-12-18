#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Password input function tests.

"""
from tinyscript.helpers.password import *

from utils import *


class TestHelpersPassword(TestCase):
    def test_getpass(self):
        # test the policy
        self.assertRaises(ValueError, getpass, policy="BAD")
        self.assertRaises(ValueError, getpass, policy={'allowed': "BAD"})
        self.assertRaises(ValueError, getpass, policy={'allowed': "?l", 'required': "?L"})
        self.assertRaises(ValueError, getpass, policy={'wordlists': "BAD"})
        for l in [(-1, 10), (10, -1), (10, 1)]:
            self.assertRaises(ValueError, getpass, policy={'length': l})
        # test a few bad passwords
        WORDLIST = "./.wordlist"
        with open(WORDLIST, 'wt') as f:
            f.write("Test4321!")
        kwargs = {'policy': {'wordlists': ["wl_does_not_exist"]}}
        for i, p in enumerate(["test", "Test1", "Test1!", "Testtest", "testtesttest", "\x01\x02\x03", "Test4321!",
                               "Th1s 1s 4 l0ng, v3ry l0ng, t00 l0ng c0mpl3x s3nt3nc3!"]):
            if i > 2:
                kwargs['policy'] = {'wordlists': [WORDLIST]}
            with mock_patch("getpass.getpass", return_value=p):
                self.assertRaises(ValueError, getpass, **kwargs)
        remove(WORDLIST)
        # test a few good passwords
        kwargs = {}
        for i, p in enumerate(["Test1234!", "Th1s 1s 4 l0ng s3nt3nc3!"]):
            if i > 1:
                kwargs['policy'] = {'wordlists': None}
            with mock_patch("getpass.getpass", return_value=p):
                pswd = getpass(**kwargs)
            self.assertEqual(pswd, p)
    
    def test_getrepass(self):
        with mock_patch("getpass.getpass", return_value="test"):
            self.assertRaises(ValueError, getrepass, pattern=r"[a-z]+\d+")
        with mock_patch("getpass.getpass", return_value="test1"):
            self.assertEqual(getrepass(pattern=r"[a-z]+\d+"), "test1")

