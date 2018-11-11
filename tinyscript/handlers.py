#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining handlers and exit hook.

"""
import logging
import signal
import sys

from .__info__ import __author__, __copyright__, __version__


__features__ = ["at_exit", "at_graceful_exit", "at_interrupt", "at_terminate"]
__all__ = ["_hooks"] + __features__


class ExitHooks(object):
    # inspired from: https://stackoverflow.com/questions/9741351/how-to-find-exi
    #                 t-code-or-reason-when-atexit-callback-is-called-in-python
    def __init__(self):
        self.code = None
        self.exception = None
        self.state = None

    def hook(self):
        self._orig_exit = sys.exit
        sys.exit = self.exit

    def exit(self, code=0):
        self.code = code
        self._orig_exit(code)

_hooks = ExitHooks()
_hooks.hook()


def __interrupt_handler(*args):
    """
    Interruption handler.

    :param signal: signal number
    :param stack: stack frame
    :param code: exit code
    """
    _hooks.state = "INTERRUPTED"
    sys.exit(0)
# bind to interrupt signal (Ctrl+C)
signal.signal(signal.SIGINT, __interrupt_handler)


def __terminate_handler(*args):
    """
    Termination handler.

    :param signal: signal number
    :param stack: stack frame
    :param code: exit code
    """
    _hooks.state = "TERMINATED"
    sys.exit(0)
# bind to terminate signal
signal.signal(signal.SIGTERM, __terminate_handler)


def at_exit():
    pass


def at_graceful_exit():
    pass


def at_interrupt():
    pass


def at_terminate():
    pass
