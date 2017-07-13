#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import argparse
import logging
import os
import random
import re
import signal
import sys
import time
# colorize logging
try:
    import coloredlogs
    colored_logs_present = True
except:
    print("(Install 'coloredlogs' for colored logging)")
    colored_logs_present = False


__all__ = [
    'LOG_FORMAT', 'DATE_FORMAT',                   # constants
    'parser',                                      # instances
    'exit_handler', 'initialize', 'validate',      # functions
    'os', 'random', 're', 'signal', 'sys', 'time', # modules
]


LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DATE_FORMAT = '%H:%M:%S'


def __descr_format(g):
    """
    Help description formatting function to add global documentation variables.

    :param g: globals() dictionary
    :return: the formatted help description
    """
    p = g['__file__']
    p = p[2:] if p.startswith("./") else p
    p = p[:-3] if p.endswith(".py") else p
    s = ''.join([x.capitalize() for x in p.split('-')])
    if '__version__' in g:
        s += " v" + g['__version__']
    for v in ['__author__', '__reference__', '__source__', '__training__']:
        if v in g:
            s += "\n%s: %s" % (v.strip('_').capitalize(), g[v])
            if v == '__author__' and '__email__' in g:
                s += " ({})".format(g['__email__'])
    return s + "\n\n" + g['__doc__'] if '__doc__' in g else s


def exit_handler(signal=None, frame=None, code=0):
    """
    Exit handler.

    :param signal: signal number
    :param stack: stack frame
    :param code: exit code
    """
    logging.shutdown()
    sys.exit(code)
# bind termination signal (Ctrl+C) to exit handler
signal.signal(signal.SIGINT, exit_handler)


def initialize(glob, sudo=False):
    """
    Initialization function ; sets up the arguments for the parser and creates a
     logger to be inserted in the input dictionary of global variables from the
     calling script.

    :param glob: globals() instance from the calling script
    """
    global args, logger, parser
    p = glob['__file__']
    p = p[2:] if p.startswith("./") else p
    e = None if '__examples__' not in glob or len(glob['__examples__']) == 0 \
        else glob['__examples__']
    e = "Usage examples:\n" + '\n'.join(["  python {0} {1}".format(p, x) \
        for x in e]) if e is not None else e
    glob['parser'] = argparse.ArgumentParser(prog=p,
        description=__descr_format(glob), epilog=e,
        formatter_class=argparse.RawTextHelpFormatter)
    glob['parser'].add_argument("-v", dest="debug", action="store_true",
                                help="debug verbose level (default: false)")
    for method, args, kwargs in parser.calls:
        getattr(glob['parser'], method)(*args, **kwargs)
    glob['args'] = parser.parse_args()
    if sudo:
        # if not root, restart the script in another process and jump to this
        if os.geteuid() != 0:
            python = [] if glob['__file__'].startswith("./") else ["python"]
            os.execvp("sudo", ["sudo"] + python + sys.argv)
    # configure logging and get the root logger
    glob['args'].verbose = [logging.INFO, logging.DEBUG][glob['args'].debug]
    logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT,
                        level=glob['args'].verbose)
    glob['args'] = logging.getLogger()
    if colored_logs_present:
        coloredlogs.DEFAULT_LOG_FORMAT = LOG_FORMAT
        coloredlogs.DEFAULT_DATE_FORMAT = DATE_FORMAT
        coloredlogs.install(args.verbose)


def validate(*arg_checks):
    """
    Function for validating group of arguments ; each argument is represented as
     a 4-tuple like follows:

        (argument_name, fail_condition, error_message, default)

        - argument_name: the name of the argument like entered in add_argument()
        - fail_condition: condition in Python code with the argument name
                          replaced by ' ? ' (e.g. " ? > 0")
        - error_message: message describing what failed with the validation ofs
                         the current argument
        - default [optional]: value to be given if the validation fails ; this
                              implies that the script will not exit after the
                              validation (if no other blocking argument present)

    :param arg_checks: list of 3/4-tuples
    """
    global args, logger
    if args is None or logger is None:
        return
    exit_app = False
    for check in arg_checks:
        check = check + (None, ) * (4 - len(check))
        param, condition, message, default = check
        if eval(condition.replace(" ? ", " args.{} ".format(param))):
            logger.error(message or "Validation failed")
            exit_app |= default is None
            if default is not None:
                setattr(args, param, default)
    if exit_app:
        exit_handler(code=2)


class ProxyArgumentParser(object):
    """
    Proxy class for collecting added arguments before initialization.
    """
    def __init__(self):
        self.calls = []
        self.__parser = argparse.ArgumentParser()

    def __getattr__(self, name):
        if hasattr(self.__parser, name) and \
            callable(getattr(self.__parser, name)):
            self.__current_call = name
            return self.__collect

    def __collect(self, *args, **kwargs):
        self.calls.append((self.__current_call, args, kwargs))
        del self.__current_call


parser = ProxyArgumentParser()
