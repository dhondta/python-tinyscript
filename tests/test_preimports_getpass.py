#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports password input assets' tests.

"""
from tinyscript.preimports import getpass

from utils import *


class TestPreimportsGetpass(TestCase):
    def test_getcompliantpass(self):
        # test the policy
        self.assertRaises(ValueError, getpass.getcompliantpass, policy="BAD")
        self.assertRaises(ValueError, getpass.getcompliantpass, policy={'allowed': "BAD"})
        self.assertRaises(ValueError, getpass.getcompliantpass, policy={'allowed': "?l", 'required': "?L"})
        self.assertRaises(ValueError, getpass.getcompliantpass, policy={'wordlists': "BAD"})
        for l in [(-1, 10), (10, -1), (10, 1)]:
            self.assertRaises(ValueError, getpass.getcompliantpass, policy={'length': l})
        # test a few bad passwords
        WORDLIST = "./.wordlist"
        with open(WORDLIST, 'wt') as f:
            f.write("Test4321!")
        kwargs = {'once': True, 'policy': {'wordlists': ["wl_does_not_exist"]}}
        for i, p in enumerate(["test", "Test1", "Test1!", "Testtest", "testtesttest", "\x01\x02\x03", "Test4321!",
                               "Th1s 1s 4 l0ng, v3ry l0ng, t00 l0ng c0mpl3x s3nt3nc3!"]):
            if i > 2:
                kwargs['policy'] = {'wordlists': [WORDLIST]}
            with mock_patch("getpass.getpass", return_value=p):
                pswd = getpass.getcompliantpass(**kwargs)
            self.assertIsNone(pswd)
        remove(WORDLIST)
        # test a few good passwords
        kwargs = {'once': True}
        for i, p in enumerate(["Test1234!", "Th1s 1s 4 l0ng s3nt3nc3!"]):
            if i > 1:
                kwargs['policy'] = {'wordlists': None}
            with mock_patch("getpass.getpass", return_value=p):
                pswd = getpass.getcompliantpass(**kwargs)
            self.assertEqual(pswd, p)

