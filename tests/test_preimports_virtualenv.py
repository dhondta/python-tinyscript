#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Virtual environment assets' tests.

"""
from tinyscript.preimports import os, virtualenv

from utils import *


REQS = "requirements-venv-test.txt"
VENV = "venv"
VENV2 = "venv2"


class TestPreimportsVirtualenv(TestCase):
    def test_virtualenv_improvements(self):
        with open(REQS, 'w') as f:
            f.write("asciistuff")
        self.assertRaises(Exception, virtualenv.activate, "venv_does_not_exist")
        virtualenv.setup(VENV, REQS)
        if exists(REQS):
            remove(REQS)
        virtualenv.setup(VENV, ["os"])
        virtualenv.install("asciistuff", "-v", progress_bar="off")
        os.environ['PIP_REQ_TRACKER'] = "/tmp/does_not_exist"
        virtualenv.setup(VENV2, ["sys"])
        self.assertRaises(Exception, virtualenv.install, "sys", error=True)
        virtualenv.teardown()
        self.assertRaises(Exception, virtualenv.install, "test")
        with virtualenv.VirtualEnv(VENV2, remove=True) as venv:
            venv.install("asciistuff")
            self.assertTrue(venv.is_installed("setuptools"))
            self.assertTrue(venv.is_installed("asciistuff"))
            self.assertIsNotNone(venv.asciistuff)
            venv.install("does_not_exist")
            self.assertFalse(venv.is_installed("does_not_exist"))
            self.assertRaises(AttributeError, getattr, venv, "does_not_exist")
        virtualenv.teardown(VENV)
        self.assertRaises(Exception, virtualenv.PipPackage, "os")

