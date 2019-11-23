#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining handlers and exit hook.

"""
import logging
import sys
from signal import signal, SIGINT, SIGTERM

from .__info__ import __author__, __copyright__, __version__


__features__ = ["at_exit", "at_graceful_exit", "at_interrupt", "at_terminate"]
__all__ = ["_hooks"] + __features__


class ExitHooks(object):
    # inspired from: https://stackoverflow.com/questions/9741351/how-to-find-exi
    #                 t-code-or-reason-when-atexit-callback-is-called-in-python
    def __init__(self):
        self._exit = True
        self._orig_exit = sys.exit
        self.code = None
        self.exception = None
        self.state = None
        sys.exit = self.exit

    def exit(self, code=0):
        self.code = code
        self._orig_exit(code)
    
    def quit(self, code=0):
        if self.state != "INTERRUPTED" or self._exit:
            self.exit(code)

_hooks = ExitHooks()


def __interrupt_handler(*args):
    """
    Interruption handler.

    :param signal: signal number
    :param stack: stack frame
    :param code: exit code
    """
    _hooks.state = "INTERRUPTED"
    _hooks.quit(0)
# bind to interrupt signal (Ctrl+C)
signal(SIGINT, __interrupt_handler)


def __terminate_handler(*args):
    """
    Termination handler.

    :param signal: signal number
    :param stack: stack frame
    :param code: exit code
    """
    _hooks.state = "TERMINATED"
    _hooks.quit(0)
# bind to terminate signal
signal(SIGTERM, __terminate_handler)


at_exit          = lambda: None
at_graceful_exit = lambda: None
at_interrupt     = lambda: None
at_terminate     = lambda: None
