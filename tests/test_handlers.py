#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Handlers module assets' tests.

"""
from subprocess import Popen, PIPE

from tinyscript import *
from tinyscript.handlers import *
from tinyscript.handlers import (signal, ExitHooks, SIGINT, SIGTERM,
                           __interrupt_handler as ih, __terminate_handler as th)

from utils import *


FILE = tmpf()
SCRIPT = """from tinyscript import *
def at_{}():
    with open("{}", 'w+') as f:
        f.write("{}")
initialize(){}"""
SIGNALS = {
    'interrupt': "SIGINT",
    'terminate': "SIGTERM",
}
TEXT = tmpf("handler-result", "txt")


def exec_script(handler):
    s = SIGNALS.get(handler)
    s = ["\nos.kill(os.getpid(), signal.{})".format(s), ""][s is None]
    with open(FILE, 'w+') as f:
        f.write(SCRIPT.format(handler.lower(), TEXT, handler.upper(), s))
    p = Popen(["python{}".format(["2", "3"][PYTHON3]), FILE])
    p.wait()
    try:
        with open(TEXT) as f:
            out = f.read().strip()
        return out
    except IOError:
        pass


class TestHandlers(TestCase):
    def _test_handler(self, h):
        self.assertEqual(exec_script(h), h.upper())
    
    @classmethod
    def tearDownClass(self):
        remove(FILE)
        remove(TEXT)

    def test_exit_handler(self):
        self.assertIs(at_exit(), None)
        self._test_handler("exit")
    
    def test_graceful_exit_handler(self):
        self.assertIs(at_graceful_exit(), None)
        self._test_handler("graceful_exit")
    
    def test_interrupt_handler(self):
        self.assertIs(at_interrupt(), None)
        self._test_handler("interrupt")
    
    def test_terminate_handler(self):
        self.assertIs(at_terminate(), None)
        self._test_handler("terminate")
    
    def test_private_handlers(self):
        self.assertRaises(SystemExit, ih)
        self.assertIsNot(signal(SIGINT, ih), None)
        self.assertRaises(SystemExit, th)
        self.assertIsNot(signal(SIGTERM, th), None)
        self.assertRaises(SystemExit, _hooks.exit)
