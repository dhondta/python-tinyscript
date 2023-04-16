#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Handlers module assets' tests.

"""
import threading

from tinyscript import *
from tinyscript.features.handlers import *
from tinyscript.features.handlers import signal, SIGINT, SIGTERM, _hooks, __interrupt_handler as ih, \
                                         __pause_handler as ph, __terminate_handler as th

from utils import *


FILE = tmpf()
SCRIPT1 = """from tinyscript import *
def at_{0}():
    with open("{1}", 'w+') as f:
        f.write("{2}")
initialize()
{3}"""
SCRIPT2 = """from tinyscript import *
def at_{0}():
    with open("{1}", 'w+') as f:
        f.write("{2}")
initialize()
with DisableSignals(signal.{2}) as _:
    {3}"""
SIGNALS = {
    'interrupt': "SIGINT",
    'terminate': "SIGTERM",
}
FILE2 = tmpf("handler-result", "txt")


def exec_pause(self):
    while _hooks.state != "PAUSED":
        sleep(.1)
    self.assertEqual(_hooks.state, "PAUSED")
    _hooks.resume()


def exec_script(handler, template):
    s = SIGNALS.get(handler)
    t = ["os.kill(os.getpid(), signal.{})".format(s), ""][s is None]
    with open(FILE, 'w+') as f:
        f.write(template.format(handler, FILE2, s, t))
    p = subprocess.Popen(["python{}".format(["2", "3"][PYTHON3]), FILE])
    p.wait()
    try:
        with open(FILE2) as f:
            out = f.read().strip()
        remove(FILE2)
        return out
    except IOError:
        pass


class TestHandlers(TestCase):
    def _test_handler(self, h):
        self.assertEqual(exec_script(h, SCRIPT1), SIGNALS.get(h))
    
    @classmethod
    def tearDownClass(self):
        remove(FILE)
    
    def test_disable_handlers(self):
        with DisableSignals(SIGINT):
            self.assertIsNone(exec_script("interrupt", SCRIPT2))
            self.assertIsNone(exec_script("terminate", SCRIPT2))
        self.assertRaises(ValueError, DisableSignals, 123456, fail=True)
    
    def test_interrupt_handler(self):
        self.assertIs(at_interrupt(), None)
        self._test_handler("interrupt")
        _hooks.sigint_action = "confirm"
        temp_stdout(self)
        temp_stdin(self, "\n")
        self.assertRaises(SystemExit, ih)
        _hooks.sigint_action = "continue"
        self.assertIsNone(ih())
        with self.assertRaises(ValueError):
            _hooks.sigint_action = "BAD_ACTION"
        self.assertIsNotNone(_hooks.sigint_action)
        _hooks.sigint_action = "exit"
    
    def test_pause_handler(self):
        #FIXME: test once the feature for pausing execution is developed
        if WINDOWS:
            logger.warning("Pause-related features are not implemented for Windows")
        else:
            from tinyscript.features.handlers import SIGUSR1
            self.assertIsNot(signal(SIGUSR1, ph), None)
            self.assertEqual(_hooks.state, "RUNNING")
            t = threading.Thread(target=exec_pause, args=(self, ))
            t.start()
            ph()
            t.join()
            self.assertEqual(_hooks.state, "RUNNING")
    
    def test_terminate_handler(self):
        self.assertIs(at_terminate(), None)
        self._test_handler("terminate")
    
    def test_private_handlers(self):
        self.assertRaises(SystemExit, ih)
        self.assertIsNot(signal(SIGINT, ih), None)
        self.assertRaises(SystemExit, th)
        self.assertIsNot(signal(SIGTERM, th), None)
        self.assertRaises(SystemExit, _hooks.exit)

