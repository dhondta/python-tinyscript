#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining argument parser-related functions and objects.

"""
import argparse
import atexit
import os
import re
import sys
from inspect import currentframe, getmembers, isfunction, ismethod
from os.path import basename, splitext
from six import string_types

from .features.handlers import _hooks
from .argreparse import *
from .features import *
from .helpers.common import is_admin
from .helpers.constants import LINUX, PYTHON3, WINDOWS
from .helpers.data.types import ip_address, port_number
from .helpers.text import configure_docformat, gt


__all__ = __features__ = ["parser", "initialize"]

AT_EXIT_SET  = False
BANNER_ARG   = None
BANNER_FONT  = None
BANNER_STYLE = {}

parser_calls = []  # will be populated by calls to ProxyArgumentParser


def _save_config(glob):
    cf = glob['args'].write_config
    if cf:
        with open(cf, 'w') as f:
            glob['parser']._config.write(f)
        glob['logger'].debug(gt("Input arguments written to file '{}'").format(cf))


def initialize(add_banner=False,
               add_config=False,
               add_demo=False,
               add_interact=False,
               add_notify=False,
               add_progress=False,
               add_step=False,
               add_time=False,
               add_version=False,
               add_wizard=False,
               sudo=False,
               multi_level_debug=False,
               short_long_help=True,
               action_at_interrupt="exit",
               ext_logging=False,
               noargs_action=None,
               post_actions=True,
               report_func=None,
               autocomplete=False,
               **kwargs):
    """
    Initialization function ; sets up the arguments for the parser and creates a logger to be inserted in the input
     dictionary of global variables from the calling script.

    :param add_banner:          add an ASCII banner when starting the tool
    :param add_config:          add an option to input an INI configuration file
    :param add_demo:            add an option to re-run the process using a random entry from the __examples__
                                 (only works if this variable is populated)
    :param add_interact:        add an interaction option
    :param add_notify:          add a notification option
    :param add_progress:        add a progress management option
    :param add_step:            add an execution stepping option
    :param add_time:            add an execution timing option
    :param add_version:         add a version option
    :param add_wizard:          add an option to run a wizard, asking for each input argument
    :param sudo:                if True, require sudo credentials and re-run script with sudo
    :param multi_level_debug:   allow to use -v, -vv, -vvv (adjust logging level) instead of just -v (only debug on/off)
    :param short_long_help:     enable/disable the separation of -h/--help
    :param action_at_interrupt: perform an action at interrupt (confirm|continue|exit)
    :param ext_logging:         extended logging options
    :param noargs_action:       action to be performed when no argument is input
    :param post_actions:        enable post-actions at interrupt
    :param report_func:         report generation function
    :param autocomplete:        add autocompletion with argcomplete
    """
    global parser, parser_calls
    # handle backward-compatibility arguments
    exit_at_interrupt = kwargs.pop('exit_at_interrupt', None)
    if len(kwargs) > 0:
        raise TypeError("Unexpected keyword-arguments (%s)" % ", ".join(kwargs.keys()))
    # get caller's frame
    frame = currentframe().f_back
    # walk the stack until a frame containing a known object is found
    glob = {}
    while frame:
        if isinstance(frame.f_globals.get('parser'), ProxyArgumentParser):
            glob = frame.f_globals
            # search for dunders
            for d in DUNDERS:
                f = frame
                while f and (d not in f.f_globals.keys() or f.f_globals[d] is None):
                    f = f.f_back
                try:
                    glob[d] = f.f_globals[d]
                except (AttributeError, KeyError):
                    pass
            break
        frame = frame.f_back
    if any(glob.get(k) is not None for k in ["NOTIFICATION_ICONS_PATH", "NOTIFICATION_LEVEL", "NOTIFICATION_TIMEOUT"]):
        add_notify = True
    add = {'config': add_config, 'demo': add_demo, 'interact': add_interact, 'notify': add_notify,
           'progress': add_progress, 'step': add_step, 'time': add_time, 'version': add_version, 'wizard': add_wizard,
           'help': True, 'usage': True}
    p = ArgumentParser(glob)
    # 1) handle action when no input argument is given
    add['demo'] = add['demo'] and p.examples
    noarg = len(sys.argv) == 1
    if noarg and noargs_action:
        if noargs_action not in add.keys():
            raise ValueError(gt("Bad action when no args (should be one of: {})").format('|'.join(add.keys())))
        add[noargs_action] = True  # ensure this action is enabled, even if it is not given the passed arguments
    # 2) populate the real parser and add information arguments
    __parsers = {parser: p}
    #  proxy parser to real parser recursive conversion function
    def __proxy_to_real_parser(value):
        """
        This recursively converts ProxyArgumentParser instances to real parsers.

        Use case: defining subparsers with a parent
          >>> [...]
          >>> parser.add_argument(...)  # argument common to all subparsers
          >>> subparsers = parser.add_subparsers()
          >>> subparsers.add_parser(..., parents=[parent])
                                                    ^
                   this is an instance of ProxyArgumentParser and must be converted to an actual parser instance

        :param value: a value coming from args or kwargs aimed to a real parser
        """
        if isinstance(value, ProxyArgumentParser):
            return __parsers[value]
        elif isinstance(value, (list, tuple)):
            return [__proxy_to_real_parser(_) for _ in value]
        return value
    #  now iterate over the registered calls
    for proxy_parser, method, args, kwargs, proxy_subparser in parser_calls:
        real_parser = __parsers[proxy_parser]
        args = (__proxy_to_real_parser(v) for v in args)
        kwargs = {k: __proxy_to_real_parser(v) for k, v in kwargs.items()}
        real_subparser = getattr(real_parser, method)(*args, **kwargs)
        if real_subparser is not None:
            __parsers[proxy_subparser] = real_subparser
    # this allows to ensure that another call to initialize(...) will have a clean list of calls and an empty _config
    #  attribute
    parser_calls = []
    ArgumentParser.reset()
    i = p.add_argument_group("extra arguments")
    # configure documentation formatting
    configure_docformat(glob)
    # config handling feature, for reading/writing an INI config file with the input arguments, e.g. for future reuse
    if add['config']:
        c = p.add_argument_group("config arguments")
        opt = c.add_argument("-r", "--read-config", action="config", help=gt("read args from a config file"),
                             note=gt("this overrides other arguments"))
        c.add_argument("-w", "--write-config", metavar="INI", help=gt("write args to a config file"))
        if noarg and noargs_action == "config":
            sys.argv[1:] = [opt, "config.ini"]
    # demonstration feature, for executing an example amongst these defined in __examples__, useful for observing what
    #  the tool does
    if add['demo']:
        opt = i.add_argument("--demo", action="demo", prefix="play", help=gt("demonstrate a random example"))
        if noarg and noargs_action == "demo":
            sys.argv[1:] = [opt]
    # help feature, for displaying classical or extended help about the tool
    if add['help']:
        if glob.get('__details__'):
            opt = i.add_argument("-h", dest="help", default=0, help=gt("show extended help message and exit"),
                                 action="count", note=gt("-hhh is the highest help detail level"))
        elif short_long_help:
            opt = i.add_argument("-h", dest="usage", action="usage", help=gt("show usage message and exit"))
            opt = i.add_argument("--help", action="help", help=gt("show this help message and exit"))
        else:
            opt = i.add_argument("-h", "--help", action="help", help=gt("show this help message and exit"))
        if noarg and noargs_action == "help":
            sys.argv[1:] = ["--help"]
        elif noarg and noargs_action == "usage":
            sys.argv[1:] = ["DISPLAY_USAGE"]
    # interaction mode feature, for interacting with the tool during its execution, useful for debugging
    if add['interact']:
        j = p.add_argument_group("interaction arguments")
        opt = j.add_argument("--interact", action="store_true", suffix="mode", help=gt("interaction mode"))
        if opt:
            j.add_argument("--host", default="127.0.0.1", type=ip_address, prefix="remote",
                           help=gt("remote interacting host"))
            j.add_argument("--port", default=12345, type=port_number, prefix="remote",
                           help=gt("remote interacting port"))
        if noarg and noargs_action == "interact":
            sys.argv[1:] = [opt]
        set_interact_items(glob)
    # notification feature, for displaying notifications during the execution
    if add['notify']:
        opt = i.add_argument("-n", "--notify", action="store_true", suffix="mode", help=gt("notify mode"))
        if noarg and noargs_action == "notify":
            sys.argv[1:] = [opt]
        set_notify_items(glob)
    # progress mode feature, for displaying a progress bar during the execution
    if add['progress']:
        opt = i.add_argument("-p", "--progress", action="store_true", suffix="mode", help=gt("progress mode"))
        if noarg and noargs_action == "progress":
            sys.argv[1:] = [opt]
        set_progress_items(glob)
    # stepping mode feature, for stepping within the tool during its execution, especially useful for debugging
    if add['step']:
        opt = i.add_argument("--step", action="store_true", last=True, suffix="mode", help=gt("stepping mode"))
        if noarg and noargs_action == "step":
            sys.argv[1:] = [opt]
        set_step_items(glob)
    # timing mode feature, for measuring time along the execution of the tool
    if add['time']:
        b = p.add_argument_group("timing arguments")
        opt = b.add_argument("--stats", action='store_true', last=True, prefix="time",
                             help=gt("display execution time stats at exit"))
        b.add_argument("--timings", action='store_true', last=True, suffix="mode",
                       help=gt("display time stats during execution"))
        if noarg and noargs_action == "time":
            sys.argv[1:] = [opt]
    # version feature, for displaying the version from __version__
    if add['version']:
        version = glob['__version__'] if '__version__' in glob else None
        if version is not None:
            opt = i.add_argument("--version", action='version', prefix="show", version=version,
                                 help=gt("show program's version number and exit"))
            if noarg and noargs_action == "version":
                sys.argv[1:] = [opt]
    # verbosity feature, for displaying debugging messages, with the possibility to handle multi-level verbosity
    if multi_level_debug:
        i.add_argument("-v", dest="verbose", default=0, action="count", suffix="mode", cancel=True, last=True,
                       help=gt("verbose level"), note=gt("-vvv is the highest verbosity level"))
    else:
        i.add_argument("-v", "--verbose", action="store_true", last=True, suffix="mode", help=gt("verbose mode"))
    # wizard feature, for asking argument values to the user
    if add['wizard']:
        opt = i.add_argument("-w", "--wizard", action="wizard", prefix="start", help=gt("start a wizard"))
        if noarg and noargs_action == "wizard":
            sys.argv[1:] = [opt]
    # reporting feature, for making a reporting with the results of the tool at the end of its execution
    if report_func is not None and PYTHON3:
        if not isfunction(report_func):
            report_func = None
            glob['logger'].error(gt("Bad report generation function"))
        else:
            # lazily import report features
            #  -> reason: they rely on weasyprint, which take time to be imported ; so, when report features are not
            #              used in a script, report classes won't be loaded
            all_list = __import__("tinyscript.report", fromlist=['__all__']).__all__
            report = __import__("tinyscript.report", fromlist=all_list)
            for f in all_list:
                glob[f] = globals()[f] = getattr(report, f)
            # now populate the parser with report-related arguments
            r = p.add_argument_group("report arguments")
            output_func = list(filter(lambda x: getattr(x[1], '_output', False), getmembers(Report)))
            choices = list(map(lambda x: x[0], output_func))
            if r.add_argument("--output", choices=choices, default="pdf", last=True, prefix="report",
                              help=gt("report output format")):
                r.add_argument("--title", last=True, prefix="report", help=gt("report title"))
                r.add_argument("--css", last=True, prefix="report", help=gt("report stylesheet file"))
                r.add_argument("--theme", default="default", last=True, prefix="report",
                               help=gt("report stylesheet theme"), note=gt("--css overrides this setting"))
                r.add_argument("--filename", last=True, prefix="report", help=gt("report filename"))
    elif report_func is not None and not PYTHON3:
        report_func = None  # disable reporting in the at_exit handler
        glob['logger'].warning(gt("Report generation is only available with Python 3"))
    # extended logging features
    if ext_logging:
        i.add_argument("-f", "--logfile", last=True, help=gt("destination log file"))
        i.add_argument("-r", "--relative", action="store_true", last=True, suffix="time",
                       help=gt("display relative time"))
        if LINUX:
            i.add_argument("-s", "--syslog", action="store_true", last=True, suffix="mode",
                           help=gt("log to /var/log/syslog"))
    # if enabled, apply argcomplete's auto-completion
    if autocomplete:
        from argcomplete import autocomplete
        autocomplete(p)
    # now parse inputs
    glob['args'], glob['parser'] = p.parse_args(), p
    # 3) if sudo required, restart the script
    if sudo and not is_admin():
        exe = ["runas", "/env", "/user:Administrator"] if WINDOWS else ["sudo", "-E"]
        os.execvp(["sudo", "runas"][WINDOWS], exe + [sys.executable] + sys.argv)
    # 4) configure logging and get the main logger
    a = glob['args']
    configure_logger(glob, multi_level_debug,
                     getattr(a, a._collisions.get("relative", "relative"), False),
                     getattr(a, a._collisions.get("logfile", "logfile"), None),
                     getattr(a, a._collisions.get("syslog", "syslog"), None))
    # 5) configure features that need it (even if not enabled)
    set_hotkeys(glob)
    set_time_items(glob)
    # 6) display a banner if relevant
    bf = glob.get('BANNER_FONT', BANNER_FONT)
    if add_banner or isinstance(bf, string_types):
        # expensive to load asciistuff ; import only when a banner is used
        from asciistuff import AsciiFile, Banner
        f = AsciiFile()
        banner = getattr(glob['args'], glob.get('BANNER_ARG', BANNER_ARG) or "", None) or p.banner
        f['title', glob.get('BANNER_STYLE', BANNER_STYLE)] = Banner(banner, font=bf)
        print(f)
    # 7) finally, bind the global exit handler
    _hooks.sigint_action = action_at_interrupt if exit_at_interrupt is None else ["continue", "exit"][exit_at_interrupt]
    def __at_exit():
        # first, dump the config if required
        if add['config']:
            _save_config(glob)
        # now, close the current progress bar (if any)
        if add['progress']:
            glob['progress_manager'].stop()
        # then handle the state
        do_post_actions = True
        if _hooks.state == "INTERRUPTED":
            glob.get('at_interrupt', lambda: None)()
            do_post_actions = post_actions
        elif _hooks.state == "TERMINATED":
            glob.get('at_terminate', lambda: None)()
            do_post_actions = False
        # finally handle post-actions
        if do_post_actions:
            if report_func is not None:
                # generate the report only when exiting gracefully, just before at_graceful_exit
                a = glob['args']
                try:
                    r = Report(*report_func(), title=a.title, filename=a.filename, css=a.css, logger=glob['logger'])
                    getattr(r, a.output)(False)
                except AttributeError:
                    pass
            t = glob['time_manager']
            if add['time'] and t._stats:
                t.stats()
            glob.get('at_graceful_exit', lambda: None)()
        glob.get('at_exit', lambda: None)()
        from logging import shutdown
        shutdown()
    if not AT_EXIT_SET:
        atexit.register(__at_exit)
        globals()['AT_EXIT_SET'] = False


class ProxyArgumentParser(object):
    """
    Proxy class for collecting added arguments before initialization.
    """
    def __getattr__(self, name):
        """ Each time a method is called, return __collect to make it capture the input arguments and keyword-arguments
             if it exists in the original parser class. """
        self.__call = name
        return self.__collect

    def __collect(self, *args, **kwargs):
        """ Capture the input arguments and keyword-arguments of the currently called method, appending a proxy
             subparser in case it should be used for mutually exclusive groups or subparsers. """
        subparser = ProxyArgumentParser()
        parser_calls.append((self, self.__call, args, kwargs, subparser))
        del self.__call
        return subparser
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass


parser = ProxyArgumentParser()

