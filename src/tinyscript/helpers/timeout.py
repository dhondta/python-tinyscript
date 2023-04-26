# -*- coding: UTF-8 -*-
"""Timeout-related functions.

"""
from contextlib import contextmanager

from .constants import WINDOWS
from ..preimports import signal


__all__ = __features__ = ["timeout", "Timeout", "TimeoutError"]


class TimeoutError(Exception):
    pass  # TimeoutError is not handled in Python 2


class Timeout(object):
    """ Timeout context manager.
    
        :param seconds: number of seconds before raising the timeout
        :param message: custom message to be displayed
        :param stop:    whether the execution must be stopped in case of timeout
    """
    def __init__(self, seconds=10, message=None, stop=False):
        self.message = message
        self.seconds = seconds
        self.stop = stop

    def __enter__(self):
        if WINDOWS:
            raise NotImplementedError("signal.SIGALRM does not exist in Windows")
        else:
            signal.signal(signal.SIGALRM, self._handler)
            signal.alarm(self.seconds)
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if WINDOWS:
            raise NotImplementedError("signal.SIGALRM does not exist in Windows")
        else:
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
        return not self.stop
    
    def _handler(self, signum, frame):
        raise TimeoutError(self.message or "Execution timeout")


def timeout(seconds=10, message=None, stop=False):
    """ Decorator for applying the Timeout context manager to a function. """
    def _wrapper1(f):
        def _wrapper2(*a, **kw):
            with Timeout(seconds, message, stop) as to:
                return f(*a, **kw)
        return _wrapper2
    return _wrapper1

