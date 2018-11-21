#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining argument parser-related functions and objects.

"""
import argparse
import atexit
import os
import random
import re
import shlex
import sys
from inspect import getmembers, isfunction, ismethod
from os.path import basename, splitext

from .__info__ import __author__, __copyright__, __version__
from .argreparse import *
from .handlers import *
from .loglib import *
from .report import Report


__all__ = __features__ = ["parser", "initialize", "validate"]


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


def initialize(glob, sudo=False, multi_debug_level=False,
               add_demo=False, add_version=False, add_wizard=False,
               noargs_action=None, report_func=None):
    """
    Initialization function ; sets up the arguments for the parser and creates a
     logger to be inserted in the input dictionary of global variables from the
     calling script.

    :param glob:              globals() instance from the calling script
    :param sudo:              if True, require sudo credentials and re-run
                               script with sudo
    :param multi_debug_level: allow to use -v, -vv, -vvv (adjust logging level)
                               instead of just -v (only debug on/off)
    :param add_demo:          add an option to re-run the process using a random
                               entry from the __examples__ (only works if this
                               variable is populated)
    :param add_version:       add a version option
    :param add_wizard:        add an option to run a wizard, asking for each
                               input argument
    :param noargs_action:     action to be performed when no argument is input
    :param report_func:       report generation function
    """
    global parser, __parsers
    
    add = {'demo': add_demo, 'help': True, 'version': add_version,
           'wizard': add_wizard}
    glob['parser'] = p = ArgumentParser(glob)
    # 1) handle action when no input argument is given
    add['demo'] = add['demo'] and glob['parser'].examples
    if len(sys.argv) == 1 and noargs_action:
        assert noargs_action in add.keys(), \
               "Bad action when no args (should be one of: {})" \
               .format('|'.join(add.keys()))
        sys.argv[1:] = ["--{}".format(noargs_action)]
        add[noargs_action] = True
    # 2) if sudo required, restart the script
    if sudo:
        # if not root, restart the script in another process and jump to this
        if os.geteuid() != 0:
            python = [] if glob['__file__'].startswith("./") else ["python"]
            os.execvp("sudo", ["sudo"] + python + sys.argv)
    # 3) populate the real parser and add information arguments
    __parsers = {}
    i = p.add_argument_group(gt("extra arguments"))
    if add['demo']:
        i.add_argument("-d", "--demo", action='demo', default=SUPPRESS,
                       help=gt("start a demo of a random example"))
    if add['help']:
        i.add_argument("-h", "--help", action='help', default=SUPPRESS,
                       help=gt("show this help message and exit"))
    if add['version']:
        version = glob['__version__'] if '__version__' in glob else None
        assert version, "__version__ is not defined"
        i.add_argument("-v", "--version", action='version', default=SUPPRESS,
                       version=version,
                       help=gt("show program's version number and exit"))
    if multi_debug_level:
        i.add_argument("-v", dest="verbose", default=0, action="count",
                       help=gt("verbose level"), cancel=True,
                       note=gt("-vvv corresponds to the highest verbose level"))
    else:
        i.add_argument("-v", "--verbose", action="store_true",
                       help=gt("verbose mode"))
    if add['wizard']:
        i.add_argument("-w", "--wizard", action='wizard', default=SUPPRESS,
                       help=gt("start a wizard"))
    if report_func is not None:
        if not isfunction(report_func):
            glob['logger'].error("Bad report generation function")
            return
        r = glob['parser'].add_argument_group(gt("report arguments"))
        choices = map(lambda x: x[0],
                      filter(lambda x: not x[0].startswith('_'),
                             getmembers(Report, predicate=ismethod)))
        if r.add_argument("--output", choices=choices, default="pdf",
                          help=gt("report output format")):
            r.add_argument("--title", help=gt("report title"))
            r.add_argument("--css", help=gt("report stylesheet file"))
            r.add_argument("--theme", default="default",
                           help=gt("report stylesheet theme"),
                           note=gt("--css overrides this setting"))
            r.add_argument("--filename", help=gt("report filename"))
    __get_calls_from_parser(parser, glob['parser'])
    glob['args'] = glob['parser'].parse_args()
    # 4) configure logging and get the main logger
    configure_logger(glob, multi_debug_level)
    # 5) finally, bind the global exit handler
    def __at_exit():
        if _hooks.state == "INTERRUPTED":
            glob['at_interrupt']()
        elif _hooks.state == "TERMINATED":
            glob['at_terminate']()
        else:
            if report_func is not None:
                # generate the report only when exiting gracefully, just before
                #  the user-defined function at_graceful_exit
                _ = glob['args']
                r = Report(*report_func(), title=_.title, filename=_.filename,
                           logger=glob['logger'], css=_.css)
                getattr(r, _.output)(False)
            glob['at_graceful_exit']()
        glob['at_exit']()
        logging.shutdown()
    atexit.register(__at_exit)


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

    :param glob:       globals() instance from the calling script
    :param arg_checks: list of 3/4-tuples
    """
    locals().update(glob)  # allows to import user-defined objects from glob
                           #  into the local scope
    if glob['args'] is None or glob['logger'] is None:
        return
    exit_app = False
    for check in arg_checks:
        check = check + (None, ) * (4 - len(check))
        param, condition, message, default = check
        assert re.match(r'^_?[a-zA-Z][a-zA-Z0-9_]*$', param) is not None, \
               "Illegal argument name"
        try:
            result = eval(condition.replace(" ? ", " glob['args'].{} "
                                            .format(param)))
        except (AssertionError, TypeError) as e:
            result = True
            message = str(e)
        if result:
            if default is None:
                glob['logger'].error(message or "Validation failed")
                exit_app = True
            else:
                glob['logger'].warn(message or "Validation failed")
                setattr(glob['args'], param, default)
    if exit_app:
        sys.exit(2)


class ProxyArgumentParser(object):
    """
    Proxy class for collecting added arguments before initialization.
    """
    def __init__(self):
        self.calls = []
        self.__parser = ArgumentParser()

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
