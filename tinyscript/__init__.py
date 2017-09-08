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
    'LOG_FORMAT', 'DATE_FORMAT',                              # constants
    'parser',                                                 # instances
    'exit_handler', 'initialize', 'validate',                 # functions
    'logging', 'os', 'random', 're', 'signal','sys', 'time',  # modules
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


def __exit_handler(signal=None, frame=None, code=0):
    """
    Exit handler.

    :param signal: signal number
    :param stack: stack frame
    :param code: exit code
    """
    logging.shutdown()
    sys.exit(code)
# bind interrupt signal (Ctrl+C) to the default exit handler
signal.signal(signal.SIGINT, __exit_handler)
# bind termination signal to the default exit handler
signal.signal(signal.SIGTERM, __exit_handler)


def __get_calls_from_parser(proxy_parser, real_parser):
    """
    This actually executes the calls registered in the ProxyArgumentParser.

    :param parser: ProxyArgumentParser instance
    """
    __parsers[proxy_parser] = real_parser
    for method, safe, args, kwargs, proxy_subparser in proxy_parser.calls:
        args = (__proxy_to_real_parser(v) for v in args)
        kwargs = {k: __proxy_to_real_parser(v) for k, v in kwargs.items()}
        real_subparser = getattr(real_parser, method)(*args, **kwargs)
        if real_subparser is not None:
            __get_calls_from_parser(proxy_subparser, real_subparser)


def __proxy_to_real_parser(value):
    """
    This recursively converts ProxyArgumentParser instances to actual parsers.

    Use case: defining subparsers with a parent
      >>> [...]
      >>> parser.add_argument(...)  # argument common to all subparsers
      >>> subparsers = parser.add_subparsers()
      >>> subparsers.add_parser(..., parents=[parent])
                                                ^
                              this is an instance of ProxyArgumentParser
                              and must be converted to an actual parser instance

    :param value: a value coming from args or kwargs aimed to an actual parser
    """
    if isinstance(value, ProxyArgumentParser):
        return __parsers[value]
    elif any(isinstance(value, t) for t in [list, tuple]):
        new_value = []
        for subvalue in iter(value):
            new_value.append(__proxy_to_real_parser(subvalue))
        return new_value
    return value


def __updated_exit_handler(signal=None, frame=None, code=0):
    __exit_handler(signal, frame, code)


def exit_handler(glob=None):
    """
    Customized exit handler decorator.

    :param glob: globals() instance from the calling script
    """
    def __wrapper(f):
        global __updated_exit_handler
        def __new_exit_handler(signal=None, frame=None, code=0, *args, **kwargs):
            f(*args, **kwargs)
            __exit_handler(signal, frame, code)
        if glob is not None:
            glob[f] = __new_exit_handler
        __updated_exit_handler = __new_exit_handler
        # rebind interrupt signal (Ctrl+C) to the new exit handler
        signal.signal(signal.SIGINT, __new_exit_handler)
        # rebind termination signal to the new exit handler
        signal.signal(signal.SIGTERM, __exit_handler)
        return __new_exit_handler
    return __wrapper


def initialize(glob, sudo=False, multi_debug_level=False, add_help=True):
    """
    Initialization function ; sets up the arguments for the parser and creates a
     logger to be inserted in the input dictionary of global variables from the
     calling script.

    :param glob: globals() instance from the calling script
    :param sudo: if True, require sudo credentials and re-run script with sudo
    :param multi_debug_level: allow to use -v, -vv, -vvv (ajust logging level)
                               instead of just -v (only debug on/off)
    :param add_help: set add_help in ArgumentParser
    """
    global parser, __parsers
    # first, format help message's variables and create the real argument parser
    p = glob['__file__']
    p = p[2:] if p.startswith("./") else p
    e = None if '__examples__' not in glob or len(glob['__examples__']) == 0 \
        else glob['__examples__']
    e = "Usage examples:\n" + '\n'.join(["  python {0} {1}".format(p, x) \
        for x in e]) if e is not None else e
    glob['parser'] = argparse.ArgumentParser(prog=p, epilog=e,
        description=__descr_format(glob), add_help=add_help,
        formatter_class=argparse.RawTextHelpFormatter)
    # then populate the real parser
    __parsers = {}
    __get_calls_from_parser(parser, glob['parser'])
    try:
        glob['parser'].add_argument("-v", dest="verbose", default=0,
            action="count" if multi_debug_level else "store_true",
            help="debug verbose level (default: {})"
                 .format(["false", "error"][multi_debug_level]))
    except argparse.ArgumentError:
        pass  # if debug argument was already passed, just ignore
    glob['args'] = glob['parser'].parse_args()
    # if sudo required, restart the script
    if sudo:
        # if not root, restart the script in another process and jump to this
        if os.geteuid() != 0:
            python = [] if glob['__file__'].startswith("./") else ["python"]
            os.execvp("sudo", ["sudo"] + python + sys.argv)
    # finally, configure logging and get the root logger
    if multi_debug_level:
        glob['args']._debug_level = [logging.ERROR, logging.WARNING,
            logging.INFO, logging.DEBUG][min(glob['args'].verbose, 3)]
    else:
        glob['args']._debug_level = [logging.INFO, logging.DEBUG] \
                                    [glob['args'].verbose]
    logging.basicConfig(format=glob['LOG_FORMAT'], datefmt=glob['DATE_FORMAT'],
                        level=glob['args']._debug_level)
    glob['logger'] = logging.getLogger()
    if colored_logs_present:
        coloredlogs.DEFAULT_LOG_FORMAT = glob['LOG_FORMAT']
        coloredlogs.DEFAULT_DATE_FORMAT = glob['DATE_FORMAT']
        coloredlogs.install(glob['args']._debug_level)


def validate(glob, *arg_checks):
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

    :param glob: globals() instance from the calling script
    :param arg_checks: list of 3/4-tuples
    """
    locals().update(glob)
    if glob['args'] is None or glob['logger'] is None:
        return
    exit_app = False
    for check in arg_checks:
        check = check + (None, ) * (4 - len(check))
        param, condition, message, default = check
        if eval(condition.replace(" ? ", " glob['args'].{} ".format(param))):
            if default is None:
                glob['logger'].error(message or "Validation failed")
                exit_app = True
            else:
                glob['logger'].warn(message or "Validation failed")
                setattr(glob['args'], param, default)
    if exit_app:
        __updated_exit_handler(code=2)


class ProxyArgumentParser(object):
    """
    Proxy class for collecting added arguments before initialization.
    """
    def __init__(self):
        self.calls = []
        self.__parser = argparse.ArgumentParser()

    def __getattr__(self, name):
        self.__current_call = name
        self.__call_exists = hasattr(self.__parser, name) and \
                             callable(getattr(self.__parser, name))
        return self.__collect

    def __collect(self, *args, **kwargs):
        subparser = ProxyArgumentParser()
        self.calls.append((self.__current_call, self.__call_exists,
                           args, kwargs, subparser))
        del self.__current_call
        del self.__call_exists
        return subparser


parser = ProxyArgumentParser()
