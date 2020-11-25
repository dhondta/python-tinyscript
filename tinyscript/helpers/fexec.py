# -*- coding: UTF-8 -*-
"""Common execution functions and decorators.

"""
import os
from functools import wraps
from multiprocessing import Process
from six import string_types
from subprocess import Popen, PIPE
from threading import Thread


__all__ = __features__ = ["apply", "execute", "filter_bin", "process", "processes_clean", "thread", "threads_clean"]


PROCESSES = []
THREADS   = []


def apply(functions, args=(), kwargs={}):
    """ Shortcut to apply a list of functions to the given arguments and keyword-arguments. """
    return [f(*args, **kwargs) for f in functions]


def execute(cmd, **kwargs):
    """ Dummy wrapper for subprocess.Popen.

    :param cmd: command string
    """
    if isinstance(cmd, string_types):
        cmd = cmd.split()
    return Popen(cmd, stdout=PIPE, stderr=PIPE, **kwargs).communicate()


def filter_bin(*binaries):
    """ Filter the input list of binaries' names.

    :param binaries: binary names
    :return:         filtered list of existing binaries
    """
    l = []
    for b in binaries:
        for p in os.environ['PATH'].split(os.path.pathsep):
            p = os.path.join(p, b)
            if os.path.exists(p) and os.access(p, os.X_OK):
                l.append(b)
    return l


def process(f):
    """ Decorator function for simply running the given function as a separate process.

    :param f: function to be run as a separate process
    """
    @wraps(f)
    def _wrapper(*args, **kwargs):
        p = Process(target=f, args=args, kwargs=kwargs)
        p.start()
        PROCESSES.append(p)
        return p
    return _wrapper


def processes_clean(terminate=False, timeout=None):
    """ Utility function to clean up the list of processes. """
    global PROCESSES
    for p in PROCESSES:
        p.terminate() if terminate else p.join(timeout)
    PROCESSES = []


def thread(f):
    """ Decorator function for simply running the given function as a separate thread.

    :param f: function to be run as a separate thread
    """
    @wraps(f)
    def _wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
        THREADS.append(t)
        return t
    return _wrapper


def threads_clean(timeout=None):
    """ Utility function to clean up the list of threads. """
    global THREADS
    for t in THREADS:
        t.join(timeout)
    THREADS = []

