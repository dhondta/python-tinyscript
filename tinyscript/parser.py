#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining argument parser-related functions and objects.

"""
import argparse
import atexit
import os
import re
import sys
from inspect import getmembers, isfunction, ismethod
from os.path import basename, splitext

from .__info__ import __author__, __copyright__, __version__
from .argreparse import *
from .timing import set_time_items
from .handlers import *
from .helpers import LINUX, PYTHON3
from .helpers.types import ip_address, port_number
from .interact import set_interact_items
from .loglib import *
from .step import set_step_items


__all__ = __features__ = ["parser", "initialize", "validate"]


def __get_calls_from_parser(proxy_parser, real_parser):
    """
    This actually executes the calls registered in the ProxyArgumentParser.

    :param proxy_parser: ProxyArgumentParser instance
    :param real_parser:  ArgumentParser instance
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


def _save_config(glob):
    cf = glob['args'].write_config
    if cf:
        with open(cf, 'w') as f:
            glob['parser']._config.write(f)
        glob['logger'].debug("Input arguments written to file "
                             "'{}'".format(cf))


def initialize(glob,
               sudo=False,
               multi_level_debug=False,
               add_config=False,
               add_demo=False,
               add_interact=False,
               add_step=False,
               add_time=False,
               add_version=False,
               add_wizard=False,
               ext_logging=False,
               noargs_action=None,
               report_func=None):
    """
    Initialization function ; sets up the arguments for the parser and creates a
     logger to be inserted in the input dictionary of global variables from the
     calling script.

    :param glob:              globals() instance from the calling script
    :param sudo:              if True, require sudo credentials and re-run
                               script with sudo
    :param multi_level_debug: allow to use -v, -vv, -vvv (adjust logging level)
                               instead of just -v (only debug on/off)
    :param relative_time:     use relative time for log messages
    :param add_config:        add an option to input an INI configuration file
    :param add_demo:          add an option to re-run the process using a random
                               entry from the __examples__ (only works if this
                               variable is populated)
    :param add_interact:      add an interaction option
    :param add_step:          add an execution stepping option
    :param add_time:          add an execution timing option
    :param add_version:       add a version option
    :param add_wizard:        add an option to run a wizard, asking for each
                               input argument
    :param ext_logging:       extended logging options
    :param noargs_action:     action to be performed when no argument is input
    :param report_func:       report generation function
    """
    global parser, __parsers
    
    add = {'config': add_config, 'demo': add_demo, 'interact': add_interact,
           'step': add_step, 'time': add_time, 'version': add_version,
           'wizard': add_wizard, 'help': True}
    p = ArgumentParser(glob)
    # 1) handle action when no input argument is given
    add['demo'] = add['demo'] and p.examples
    noarg = len(sys.argv) == 1
    if noarg and noargs_action:
        if noargs_action not in add.keys():
            raise ValueError("Bad action when no args (should be one of: {})"
                             .format('|'.join(add.keys())))
        add[noargs_action] = True  # ensure this action is enabled, even if it
                                   #  is not given the passed arguments
    # 2) populate the real parser and add information arguments
    __parsers = {}
    __get_calls_from_parser(parser, p)
    #  config handling feature, for reading/writing an INI config file with the
    #   input arguments, e.g. for future reuse
    if add['config']:
        c = p.add_argument_group(gt("config arguments"))
        opt = c.add_argument("-r", "--read-config", action='config',
                             help=gt("read args from a config file"),
                             note=gt("this overrides other arguments"))
        c.add_argument("-w", "--write-config", metavar="INI",
                       help=gt("write args to a config file"))
        if noarg and noargs_action == "config":
            sys.argv[1:] = [opt, "config.ini"]
    i = p.add_argument_group(gt("extra arguments"))
    #  demonstration feature, for executing an example amongst these defined in
    #   __examples__, useful for observing what the tool does
    if add['demo']:
        opt = i.add_argument("--demo", action='demo', prefix="play",
                             help=gt("demonstrate a random example"))
        if noarg and noargs_action == "demo":
            sys.argv[1:] = [opt]
    #  help feature, for displaying classical or extended help about the tool
    if add['help']:
        if glob.get('__details__'):
            opt = i.add_argument("-h", dest="help", default=0, action="count",
                               help=gt("show extended help message and exit"),
                               note=gt("-hhh is the highest help detail level"))
        else:
            opt = i.add_argument("-h", "--help", action='help', prefix="show",
                                 help=gt("show this help message and exit"))
        if noarg and noargs_action == "help":
            sys.argv[1:] = [opt]
    #  interaction mode feature, for interacting with the tool during its
    #   execution, useful for debugging when it is complex
    if add['interact']:
        j = p.add_argument_group(gt("interaction arguments"))
        opt = j.add_argument("--interact", action="store_true",
                             suffix="mode", help=gt("interaction mode"))
        if opt:
            j.add_argument("--host", default="127.0.0.1", type=ip_address,
                           prefix="remote", help=gt("remote interacting host"))
            j.add_argument("--port", default=12345, type=port_number,
                           prefix="remote", help=gt("remote interacting port"))
        if noarg and noargs_action == "interact":
            sys.argv[1:] = [opt]
    #  stepping mode feature, for stepping within the tool during its execution,
    #   especially useful for debugging when it is complex
    if add['step']:
        opt = i.add_argument("--step", action="store_true", last=True,
                             suffix="mode", help=gt("stepping mode"))
        if noarg and noargs_action == "step":
            sys.argv[1:] = [opt]
    #  timing mode feature, for measuring time along the execution of the tool
    if add['time']:
        b = p.add_argument_group(gt("timing arguments"))
        opt = b.add_argument("--stats", action='store_true', last=True,
                             prefix="time",
                             help=gt("display execution time stats at exit"))
        b.add_argument("--timings", action='store_true', last=True,
                       suffix="mode",
                       help=gt("display time stats during execution"))
        if noarg and noargs_action == "time":
            sys.argv[1:] = [opt]
    #  version feature, for displaying the version from __version__
    if add['version']:
        version = glob['__version__'] if '__version__' in glob else None
        if version is not None:
            opt = i.add_argument("--version", action='version', prefix="show",
                                 version=version, help=gt("show program's "
                                                  "version number and exit"))
            if noarg and noargs_action == "version":
                sys.argv[1:] = [opt]
    #  verbosity feature, for displaying debugging messages, with the
    #   possibility to handle multi-level verbosity
    if multi_level_debug:
        i.add_argument("-v", dest="verbose", default=0, action="count",
                       suffix="mode", cancel=True, last=True,
                       help=gt("verbose level"),
                       note=gt("-vvv is the highest verbosity level"))
    else:
        i.add_argument("-v", "--verbose", action="store_true", last=True,
                       suffix="mode", help=gt("verbose mode"))
    #  wizard feature, for asking argument values to the user
    if add['wizard']:
        opt = i.add_argument("-w", "--wizard", action='wizard',
                             prefix="start", help=gt("start a wizard"))
        if noarg and noargs_action == "wizard":
            sys.argv[1:] = [opt]
    #  reporting feature, for making a reporting with the results of the tool
    #   at the end of its execution
    if report_func is not None and PYTHON3:
        if not isfunction(report_func):
            report_func = None
            glob['logger'].error("Bad report generation function")
            return
        # lazily import report features
        #  -> reason: they rely on pandas and weasyprint, which take time to be
        #              imported ; so, when report features are not used in a
        #              script, report classes won't be loaded
        all_list = __import__("tinyscript.report", fromlist=['__all__']).__all__
        report = __import__("tinyscript.report", fromlist=all_list)
        for f in all_list:
            glob[f] = globals()[f] = getattr(report, f)
        # now populate the parser with report-related arguments
        r = p.add_argument_group(gt("report arguments"))
        output_func = list(filter(lambda x: not x[0].startswith('_'),
                                  getmembers(Report, predicate=isfunction)))
        choices = list(map(lambda x: x[0], output_func))
        if r.add_argument("--output", choices=choices, default="pdf", last=True,
                          prefix="report", help=gt("report output format")):
            r.add_argument("--title", last=True, prefix="report",
                           help=gt("report title"))
            r.add_argument("--css", last=True, prefix="report",
                           help=gt("report stylesheet file"))
            r.add_argument("--theme", default="default", last=True,
                           prefix="report", help=gt("report stylesheet theme"),
                           note=gt("--css overrides this setting"))
            r.add_argument("--filename", last=True, prefix="report",
                           help=gt("report filename"))
    elif report_func is not None and not PYTHON3:
        glob['logger'].warning("Report generation is only for Python 3")
    # extended logging features
    if ext_logging:
        i.add_argument("-f", "--logfile", last=True,
                       help=gt("destination log file"))
        i.add_argument("-r", "--relative", action="store_true", last=True,
                       suffix="time", help=gt("display relative time"))
        if LINUX:
            i.add_argument("-s", "--syslog", action="store_true", last=True,
                           suffix="mode", help=gt("log to /var/log/syslog"))
    glob['args'], glob['parser'] = p.parse_args(), p
    # 3) if sudo required, restart the script
    if sudo:
        # if not root, restart the script in another process and jump to this
        if os.geteuid() != 0:
            python = [] if glob['__file__'].startswith("./") else ["python"]
            os.execvp("sudo", ["sudo"] + python + sys.argv)
    # 4) configure logging and get the main logger
    configure_logger(glob, multi_level_debug,
                     glob['args']._collisions.get("relative"),
                     glob['args']._collisions.get("logfile"),
                     glob['args']._collisions.get("syslog"))
    # 5) append modes items
    set_interact_items(glob)
    set_step_items(glob)
    set_time_items(glob)
    # 6) finally, bind the global exit handler
    def __at_exit():
        # first, dump the config if required
        if add['config']:
            _save_config(glob)
        # then handle the state
        if _hooks.state == "INTERRUPTED":
            glob['at_interrupt']()
        elif _hooks.state == "TERMINATED":
            glob['at_terminate']()
        else:
            if report_func is not None and PYTHON3:
                # generate the report only when exiting gracefully, just before
                #  the user-defined function at_graceful_exit
                _ = glob['args']
                r = Report(*report_func(), title=_.title, filename=_.filename,
                           logger=glob['logger'], css=_.css)
                getattr(r, _.output)(False)
            t = glob['time_manager']
            if add['time'] and t._stats:
                t.stats()
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
        if re.match(r'^_?[a-zA-Z][a-zA-Z0-9_]*$', param) is None:
            raise ValueError("Illegal argument name")
        try:
            result = eval(condition.replace(" ? ", " glob['args'].{} "
                                            .format(param)))
        except Exception as e:
            result = True
            message = str(e)
        if result:
            if default is None:
                glob['logger'].error(message or "Validation failed")
                exit_app = True
            else:
                glob['logger'].warning(message or "Validation failed")
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
    
    def reset(self):
        ArgumentParser.reset()
        self.calls = []


parser = ProxyArgumentParser()
