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

NOARGS_ACTIONS = ["demo", "help", "version", "wizard"]


def __descr_format(g):
    """
    Help description formatting function to add global documentation variables.

    :param g: globals() dictionary
    :return: the formatted help description
    """
    p, _ = splitext(basename(g['__file__']))
    s = ''.join([x.capitalize() for x in p.split('-')])
    if '__version__' in g:
        s += " v" + g['__version__']
    for v in ['__author__', '__reference__', '__source__', '__training__']:
        if v in g:
            s += "\n%s: %s" % (v.strip('_').capitalize(), g[v])
            if v == '__author__' and '__email__' in g:
                s += " ({})".format(g['__email__'])
    d = g.get('__doc__')
    return s + "\n\n" + d if d is not None else s


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


def initialize(glob, sudo=False, multi_debug_level=False, add_help=True,
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
    :param add_help:          set add_help in ArgumentParser
    :param add_demo:          add an option to re-run the process using a random
                               entry from the __examples__ (only works if this
                               variable is populated)
    :param add_version:       add an option for displaying the version
    :param add_wizard:        add an option to run a wizard, asking for each
                               input argument
    :param noargs_action:     action to be performed when no argument is input
    :param report_func:       report generation function
    """
    global parser, __parsers
    
    def add_argument(parser, *args, **kwargs):
        cancel = kwargs.pop('cancel', False)
        try:
            parser.add_argument(*args, **kwargs)
            return True
        except ArgumentError:
            l = len(args)  # e.g. args = ('-v', '--verbose')  =>  2
            args = [a.startswith('--') for a in args]  # e.g. ('--verbose', )
            if 0 < len(args) < l and not cancel:
                return add_argument(*args, **kwargs)
        return False
    
    # 1) handle action when no input argument is given
    e = None if '__examples__' not in glob or len(glob['__examples__']) == 0 \
        else glob['__examples__']
    add_demo = add_demo and e is not None
    if len(sys.argv) == 1 and noargs_action is not None:
        assert noargs_action in NOARGS_ACTIONS, \
               "Bad action when no args (should be one of: {})" \
               .format('|'.join(NOARGS_ACTIONS))
        if noargs_action == "demo":
            argv = random.choice(glob['__examples__']).replace("--demo", "")
            sys.argv[1:] = shlex.split(argv)
        else:
            sys.argv[1:] = ["--{}".format(noargs_action)]
        locals()['add_{}'.format(noargs_action)] = True
    # 2) if sudo required, restart the script
    if sudo:
        # if not root, restart the script in another process and jump to this
        if os.geteuid() != 0:
            python = [] if glob['__file__'].startswith("./") else ["python"]
            os.execvp("sudo", ["sudo"] + python + sys.argv)
    # 3) format help message's variables and create the real argument parser
    p = basename(glob['__file__'])
    pn, _ = splitext(p)
    e = gt("Usage examples") + ":\n" + '\n'.join(["  python {0} {1}".format(p, x) \
        for x in e]) if e is not None else e
    glob['parser'] = ArgumentParser(prog=pn, epilog=e,
        description=__descr_format(glob), add_help=False,
        formatter_class=HelpFormatter, conflict_handler="resolve")
    # 4) populate the real parser and add information arguments
    __parsers = {}
    info = glob['parser'].add_argument_group(gt("extra arguments"))
    if add_demo:
        add_argument(info, "-d", "--demo", action="store_true",
                     help=gt("start a demo of a random example"),
                     note=gt("this has the precedence on any other option"))
    if add_help:
        add_argument(info, "-h", "--help", action='help', default=SUPPRESS,
                     help=gt("show this help message and exit"))
    if add_version:
        version = glob['__version__'] if '__version__' in glob else None
        assert version is not None, "__version__ is not defined"
        add_argument(info, "-v", "--version", action='version',
                     default=SUPPRESS, version=version,
                     help=gt("show program's version number and exit"))
    if multi_debug_level:
        add_argument(info, "-v", dest="verbose", default=0, action="count",
                     help=gt("verbose level"), cancel=True,
                     note=gt("-vvv corresponds to the lowest verbose level"))
    else:
        add_argument(info, "-v", "--verbose", action="store_true",
                     help=gt("verbose mode"))
    if add_wizard:
        add_argument(info, "-w", "--wizard", action="store_true",
                     help=gt("start a wizard"))
    if report_func is not None:
        if not isfunction(report_func):
            glob['logger'].error("Bad report generation function")
            return
        rpt = glob['parser'].add_argument_group(gt("report arguments"))
        choices = map(lambda x: x[0],
                      filter(lambda x: not x[0].startswith('_'),
                             getmembers(Report, predicate=ismethod)))
        if add_argument(rpt, "-o", "--output", choices=choices, default="pdf",
                        help=gt("report output format")):
            add_argument(rpt, "-t", "--title", help=gt("report title"))
            add_argument(rpt, "-f", "--filename", help=gt("report filename"))
    __get_calls_from_parser(parser, glob['parser'])
    # now, handle the demo first if relevant
    if add_demo and "--demo" in sys.argv:
        argv = random.choice(glob['__examples__']).replace("--demo", "")
        sys.argv[1:] = shlex.split(argv)
    # otherwise, handle the wizard if relevant
    elif add_wizard and args.wizard:
        pass
        #TODO: parse each possible argument, using its default value if not set   
        #       in user input, using os.execvp once all new arguments have been
        #       entered by the user
    glob['args'] = glob['parser'].parse_args()
    # 5) configure logging and get the main logger
    configure_logger(glob, multi_debug_level)
    # 6) finally, bind the global exit handler
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
                           logger=glob['logger'])
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
