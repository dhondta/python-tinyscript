#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Test utility functions.

"""
import logging
import sys
from contextlib import contextmanager
from os import remove
from os.path import exists
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from tinyscript.helpers import PYTHON3
from unittest import TestCase


__all__ = ["args", "capture", "exists", "logger", "remove", "sys", "temp_stdin",
           "temp_stdout", "tmpf", "TestCase", "PYTHON3"]


tmpf = lambda name="test", ext="py": "/tmp/tinyscript-{}.{}".format(name, ext)


@contextmanager
def capture():
    stdout, stderr = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = StringIO(), StringIO()
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = stdout, stderr


def temp_stdin(tc, inputs):
    stdin = sys.stdin

    def clean():
        sys.stdin = stdin

    tc.addCleanup(clean)
    sys.stdin = StringIO(inputs)


def temp_stdout(tc):
    stdout, stderr = sys.stdout, sys.stderr

    def clean():
        sys.stdout, sys.stderr = stdout, stderr

    tc.addCleanup(clean)
    sys.stdout, sys.stderr = StringIO(), StringIO()


class FakeNamespace(object):
    _collisions = {}


args = FakeNamespace()
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())
