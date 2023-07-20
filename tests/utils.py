 #!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Test utility functions.

"""
import logging
import sys
from argparse import Action
from os import makedirs, remove as os_remove, rmdir as os_rmdir
from os.path import dirname, exists, join
from shutil import rmtree as shutil_rmtree
from six import StringIO
from time import sleep
from tinyscript.helpers.constants import PYTHON3, WINDOWS
from tinyscript.helpers.decorators import failsafe
from unittest import TestCase
try:
    from unittest.mock import patch as mock_patch
except ImportError:
    from mock import patch as mock_patch


__all__ = ["args", "dirname", "dummy_function", "dummy_lambda", "dummy_sleep", "exists", "join", "logger", "logging",
           "makedirs", "mock_patch", "remove", "rmdir", "rmtree", "sleep", "sys", "temp_stdin", "touch", "temp_stdout",
           "tmpf", "FakeLogRecord", "FakeNamespace", "TestCase", "_FakeParserAction", "FIXTURES", "PYTHON3", "WINDOWS"]


FIXTURES = {
    '__author__':       "John Doe",
    '__contributors__': [
        {'author': "James McAdams", 'email': "j.mcadams@hotmail.com"},
        {'author': "h4x0r1234", 'reason': "for his kind testing"},
        {'reason': "won't be displayed (no author and no email specified)"},
    ],
    '__copyright__':    "test",
    '__credits__':      "Thanks to Bob for his contribution",
    '__doc__':          "test tool",
    '__email__':        "john.doe@example.com",
    '__examples__':     ["-v"],
    '__license__':      "agpl-v3.0",
    '__status__':       "beta",
    '__version__':      "1.2.3",
}


dummy_lambda = lambda *a, **k: None
remove = failsafe(os_remove)
rmdir = failsafe(os_rmdir)
rmtree = failsafe(shutil_rmtree)
tmpf = lambda name="test", ext="py": ".tinyscript-{}.{}".format(name, ext)


def dummy_function(*a, **k):
    pass


def dummy_sleep(*a, **k):
    sleep(2)
    return "TEST"


def temp_stdin(tc, inputs):
    """ Temporary stdin test-case function. """
    stdin = sys.stdin

    def clean():
        sys.stdin = stdin

    tc.addCleanup(clean)
    sys.stdin = StringIO(inputs)


def temp_stdout(tc):
    """ Temporary stdout/stderr test-case function. """
    stdout, stderr = sys.stdout, sys.stderr

    def clean():
        sys.stdout, sys.stderr = stdout, stderr

    tc.addCleanup(clean)
    sys.stdout, sys.stderr = StringIO(), StringIO()


def touch(*filenames):
    """ Dummy touch file function. """
    for fn in filenames:
        with open(fn, 'w') as f:
            f.write("")


class FakeLogRecord(object):
    """ Fake log record class for testing logging. """
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
    """ Fake namespace class for testing parsing. """
    _collisions = {}


class _FakeParserAction(Action):
    """ Fake parser action class for testing parsing. """
    def __init__(self, *args, **kwargs):
        super(_FakeParserAction, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        pass

args = FakeNamespace()
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())

