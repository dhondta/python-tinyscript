# -*- coding: UTF-8 -*-
"""Common execution functions and decorators.

"""
import os
import re
import sys
from functools import wraps
from inspect import currentframe
from multiprocessing import Process
from shlex import split
from six import string_types
from subprocess import Popen, PIPE
from threading import Thread
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

from .compat import b, ensure_str


__all__ = __features__ = ["apply", "execute", "execute_and_log", "execute_and_kill", "filter_bin", "process",
                          "processes_clean", "thread", "threads_clean"]


PROCESSES = []
THREADS   = []


def __set_cmd(cmd, **kwargs):
    sh = kwargs.get('shell', False)
    if isinstance(cmd, string_types):
        if not sh:
            cmd = split(cmd)
    elif isinstance(cmd, (list, tuple)):
        cmd = " ".join(cmd) if sh else [str(x) for x in cmd]
    else:
        cmd = str(cmd)
    return cmd


def apply(functions, args=(), kwargs={}):
    """ Shortcut to apply a list of functions to the given arguments and keyword-arguments. """
    return [f(*args, **kwargs) for f in functions]


def execute(cmd, **kwargs):
    """ Dummy wrapper for subprocess.Popen.

    :param cmd: command string
    """
    rc = kwargs.pop("returncode", False)
    p = Popen(__set_cmd(cmd, **kwargs), stdout=PIPE, stderr=PIPE, **kwargs)
    out, err = p.communicate()
    return (out, err, p.returncode) if rc else (out, err)


def execute_and_log(cmd, out_maxlen=256, silent=None, **kwargs):
    """ Wrapper for subprocess.Popen, logging execution using the logger from kwargs or globals.

    :param cmd:        command string
    :param out_maxlen: convenience length limit for displaying the output of a command with logger.debug
    :param silent:     list of patterns for stderr lines to be silenced
    """
    logger, frame = kwargs.pop('logger', None), currentframe()
    while logger is None and frame is not None:
        logger = frame.f_globals.get('logger')
        frame = frame.f_back
    if logger is not None:
        logger.debug(cmd)
    out, err, retc = execute(cmd, returncode=True, **kwargs)
    if logger is not None:
        if out and len(out) < out_maxlen:
            logger.debug(ensure_str(out).strip())
        if err:
            err = ensure_str(err).strip()
            if all(re.search(pattern, err) is None for pattern in (silent or [])):
                (logger.warning if err.startswith("WARNING") else logger.error)(err)
    return out, err, retc


def execute_and_kill(cmd, patterns=None, **kwargs):
    """ Wrapper for subprocess.Popen, watching stderr for the given pattern for killing the process.

    :param cmd:      command string
    :param patterns: list of patterns for stderr lines to be watched for
    """
    def _read(pipe, queue):
        try:
            with pipe:
                for line in iter(pipe.readline, b""):
                    queue.put((pipe, line))
        finally:
            queue.put(None)
    
    bs, out, err = kwargs.pop('bufsize', 1), b"", b""
    patterns = [b(x) for x in (patterns or [])]
    p, q = Popen(__set_cmd(cmd, **kwargs), stdout=PIPE, stderr=PIPE, bufsize=bs, **kwargs), Queue()
    Thread(target=_read, args=(p.stdout, q)).start()
    Thread(target=_read, args=(p.stderr, q)).start()
    br = False
    for _ in range(2):
        for src, l in iter(q.get, None):
            if src is p.stdout:
                out += l
            else:
                err += l
                if any(pat in l for pat in patterns):
                    p.kill()
                    br = True
                    break
        if br:
            break
    return out, err, p.poll()


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

