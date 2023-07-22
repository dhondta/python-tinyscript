#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining handlers and exit hook.

"""
import sys
from signal import getsignal, signal, SIG_IGN, SIGINT, SIGTERM

from ..helpers.constants import WINDOWS


__features__ = ["at_exit", "at_graceful_exit", "at_interrupt", "at_terminate", "DisableSignals"]
__all__ = ["_hooks"] + __features__


class DisableSignals(object):
    """ Context manager that disable signal handlers.

    :param signals: list of signal identifiers
    :param fail:    whether execution should fail or not when a bad signal ID is encountered
    """
    def __init__(self, *signals, **kwargs):
        self.__handlers = {}
        for s in signals:
            try:
                self.__handlers[s] = getsignal(s)
            except ValueError as e:
                if kwargs.get('fail', False):
                    raise e

    def __enter__(self):
        for s in self.__handlers.keys():
            signal(s, SIG_IGN)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for s, h in self.__handlers.items():
            signal(s, h)


# https://stackoverflow.com/questions/9741351/how-to-find-exit-code-or-reason-when-atexit-callback-is-called-in-python
class ExitHooks(object):
    sigint_actions = ["confirm", "continue", "exit"]
    def __init__(self):
        self.__sigint_action = "exit"
        self._orig_exit = sys.exit
        self.code = None
        self.exception = None
        sys.exit = self.exit
        self.resume()
    
    def exit(self, code=0):
        self.code = code
        self._orig_exit(code)
    
    def pause(self):
        self.state = "PAUSED"
        while self.state == "PAUSED": continue
    
    def quit(self, code=0):
        from ..helpers.inputs import user_input
        if self.__sigint_action == "confirm" and \
           user_input("Do you really want to interrupt execution ?", ["(Y)es", "(N)o"], "y", style="bold") == "yes":
            self.__sigint_action = "exit"
        if self.state != "INTERRUPTED" or self.__sigint_action == "exit":
            self.exit(code)
        self.resume()
    
    def resume(self):
        self.state = "RUNNING"
    
    @property
    def sigint_action(self):
        return self.__sigint_action
    
    @sigint_action.setter
    def sigint_action(self, value):
        if value not in self.sigint_actions:
            raise ValueError("Bad interrupt action ; should be one of {}".format("|".join(self.sigint_actions)))
        self.__sigint_action = value

_hooks = ExitHooks()


def __interrupt_handler(*args):
    """ Interruption handler.

    :param signal: signal number
    :param stack: stack frame
    :param code: exit code
    """
    _hooks.state = "INTERRUPTED"
    _hooks.quit(0)
# bind to interrupt signal (Ctrl+C)
signal(SIGINT, __interrupt_handler)


def __pause_handler(*args):
    """ Execution pause handler. """
    _hooks.pause()
if not WINDOWS:
    from signal import siginterrupt, SIGUSR1
    # bind to user-defined signal
    signal(SIGUSR1, __pause_handler)
    siginterrupt(SIGUSR1, False)


def __terminate_handler(*args):
    """ Termination handler.

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

