#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Test utility functions.

"""
import logging
import sys
from argparse import Action
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
           "temp_stdout", "tmpf", "FakeLogRecord", "FakeNamespace", "TestCase",
           "PYTHON3", "_FakeParserAction"]


tmpf = lambda name="test", ext="py": ".tinyscript-{}.{}".format(name, ext)


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


class FakeLogRecord(object):
    def __init__(self):
        self.exc_info        = None
        self.exc_text        = ""
        self.levelname       = "INFO"
        self.msecs           = 0
        self.relativeCreated = 0
        self.stack_info      = None

    def __str__(self):
        return ""

    def getMessage(self):
        return ""


class FakeNamespace(object):
    _collisions = {}


class _FakeParserAction(Action):
    def __init__(self, *args, **kwargs):
        super(_FakeParserAction, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        pass

args = FakeNamespace()
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())
