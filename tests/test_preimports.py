#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports module assets' tests.

"""
from shutil import rmtree
from tinyscript.preimports import *
from tinyscript.preimports import _load_preimports

from utils import *


FILE = "test-file.txt"
REQS = "requirements-venv-test.txt"
VENV = "venv"
VENV2 = "venv2"


class TestPreimports(TestCase):
    def test_preimports(self):
        BAD = "does_not_exist"
        _load_preimports(BAD)
        self.assertIn(BAD, __badimports__)
        for m in __preimports__:
            self.assertIn(m, globals().keys())
        for m in __badimports__:
            self.assertNotIn(m, globals().keys())

    def test_hashlib_improvements(self):
        touch(FILE)
        self.assertEqual(hashlib.hash_file(FILE),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        self.assertEqual(hashlib.sha256_file(FILE),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        with open(FILE, 'w') as f:
            f.write(100 * "A")
        self.assertEqual(hashlib.hash_file(FILE, "md5"),
                         "8adc5937e635f6c9af646f0b23560fae")
        self.assertRaises(IOError, hashlib.hash_file, "does_not_exist")
        self.assertRaises(ValueError, hashlib.hash_file, FILE,
                          "not_existing_hash_algo")
        remove(FILE)
    
    def test_virtualenv_improvements(self):
        with open(REQS, 'w') as f:
            f.write("os\nsys")
        self.assertRaises(Exception, virtualenv.activate, "venv_does_not_exist")
        virtualenv.setup(VENV, REQS)
        remove(REQS)
        virtualenv.setup(VENV, ["os"])
        virtualenv.install("re", progress_bar="off")
        os.environ['PIP_REQ_TRACKER'] = "/tmp/does_not_exist"
        virtualenv.setup(VENV2, ["sys"])
        self.assertRaises(Exception, virtualenv.install, "sys", "-v")
        virtualenv.teardown()
        self.assertRaises(Exception, virtualenv.install, "test")
        with VirtualEnv(VENV2, remove=True) as venv:
            venv.install("re")
            self.assertTrue(venv.is_installed("setuptools"))
        virtualenv.teardown(VENV)
