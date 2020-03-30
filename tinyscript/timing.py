#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining benchmark mode logic.

"""
import signal
import time
from errno import ETIME
from os import strerror

from .helpers.timeout import TimeoutError


__all__ = ["set_time_items"]

TO_MSG = strerror(ETIME)


def set_time_items(glob):
    """
    This function prepares the benchmark items for inclusion in main script's
     global scope.
    
    :param glob: main script's global scope dictionary reference
    """
    a = glob['args']
    l = glob['logger']
    # Time manager, for keeping track of collected times
    class __TimeManager(object):
        """ Simple time manager, using time module. """
        def __init__(self):
            c = a._collisions
            self._stats = getattr(a, c.get("stats") or "stats", False)
            self._timings = getattr(a, c.get("timings") or "timings", False)
            self.enabled = self._stats or self._timings
            self.last = self.start = time.time()
            self.times = []
        
        def stats(self):
            end = time.time()
            b = ""
            for d, s, e in self.times:
                b += "\n{}\n> {} seconds".format(d, e - s)
            l.time("Total time: {} seconds{}".format(end - self.start, b))
    glob['time_manager'] = manager = __TimeManager()
    # private function to keep time measure in the time manager
    def _take_time(start=None, descr=None):
        t = manager.last = time.time()
        if start is not None and descr is not None:
            manager.times.append((descr, float(start), float(t)))
        return t - (start or 0)
    # Time context manager, for easilly benchmarking a block of code
    class Timer(object):
        def __init__(self, description=None, message=TO_MSG, timeout=None,
                     fail_on_timeout=False):
            self.fail = fail_on_timeout
            self.id = len(manager.times)
            self.descr = "#" + str(self.id) + \
                         (": " + (description or "")).rstrip(": ")
            self.message = message
            self.start = _take_time()
            self.timeout = timeout

        def __enter__(self):
            if manager.enabled:
                if self.timeout is not None:
                    signal.signal(signal.SIGALRM, self._handler)
                    signal.alarm(self.timeout)
                if manager._timings and self.descr:
                    l.time(self.descr)
                return self
        
        def __exit__(self, exc_type, exc_value, exc_traceback):
            if manager.enabled:
                d = _take_time(self.start, self.descr)
                if manager._timings:
                    l.time("> Time elapsed: {} seconds".format(d))
                if self.timeout is not None:
                    if not self.fail and exc_type is TimeoutError:
                        return True  # this allows to let the execution continue
            # implicitely returns None ; this lets the exception be raised
        
        def _handler(self, signum, frame):
            raise TimeoutError(self.message)
    
    glob['Timer'] = Timer
    # timing function for getting a measure from the start of the execution
    def get_time(message=None, start=manager.start):
        if manager._timings:
            l.time("> {}: {} seconds".format(message or "Time elapsed since "
                                          "execution start", _take_time(start)))
    glob['get_time'] = get_time
    # timing function for getting a measure since the last one
    def get_time_since_last(message=None):
        get_time(message or "Time elapsed since last measure", manager.last)
    glob['get_time_since_last'] = get_time_since_last
