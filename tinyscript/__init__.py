#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# modules not to be pre-imported
import atexit
import codecs
import importlib
# colorize logging
try:
    import coloredlogs
    colored_logs_present = True
except ImportError:
    print("(Install 'coloredlogs' for colored logging)")
    colored_logs_present = False

# modules to be pre-imported in the main script using tinyscript
PREIMPORTS = [
    "argparse",
    "binascii",
    "itertools",
    "logging",
    "os",
    "random",
    "re",
    "signal",
    "string",
    "sys",
    "time",
]


for module in PREIMPORTS:
    globals()[module] = importlib.import_module(module)


__all__ = [
    'LOG_FORMAT', 'DATE_FORMAT', 'PYTHON3',                        # constants
    'logger', 'parser',                                            # instances
    'at_exit', 'at_graceful_exit', 'at_interrupt', 'at_terminate', # handlers
    'initialize', 'validate', 'b', 'byteindex', 'iterbytes',       # functions
] + PREIMPORTS                                                     # modules


PYTHON3 = sys.version_info > (3,)
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DATE_FORMAT = '%H:%M:%S'


# setup a default logger for allowing logging before initialize() is called
logger = logging.getLogger("main")
if colored_logs_present:
    coloredlogs.DEFAULT_LOG_FORMAT = LOG_FORMAT
    coloredlogs.DEFAULT_DATE_FORMAT = DATE_FORMAT
    coloredlogs.install(logger=logger)


# see: http://python3porting.com/problems.html
b = lambda s: codecs.latin_1_encode(s)[0] if PYTHON3 else s
byteindex = lambda d, i=None: d[i] if PYTHON3 else ord(d[i])
iterbytes = lambda d: iter(d) if PYTHON3 else [ord(c) for c in d]


class ExitHooks(object):
    # inspired from: https://stackoverflow.com/questions/9741351/how-to-find-exi
    #                 t-code-or-reason-when-atexit-callback-is-called-in-python
    def __init__(self):
        self.code = None
        self.exception = None
        self.state = None

    def hook(self):
        self._orig_exit = sys.exit
        sys.exit = self.exit

    def exit(self, code=0):
        self.code = code
        self._orig_exit(code)

__hooks = ExitHooks()
__hooks.hook()


def __descr_format(g):
    """
    Help description formatting function to add global documentation variables.

    :param g: globals() dictionary
    :return: the formatted help description
    """
    p, _ = os.path.splitext(os.path.basename(g['__file__']))
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


def __interrupt_handler(*args):
    """
    Interruption handler.

    :param signal: signal number
    :param stack: stack frame
    :param code: exit code
    """
    __hooks.state = "INTERRUPTED"
    sys.exit(0)
# bind to interrupt signal (Ctrl+C)
signal.signal(signal.SIGINT, __interrupt_handler)


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


def __terminate_handler(*args):
    """
    Termination handler.

    :param signal: signal number
    :param stack: stack frame
    :param code: exit code
    """
    __hooks.state = "TERMINATED"
    sys.exit(0)
# bind to terminate signal
signal.signal(signal.SIGTERM, __terminate_handler)


def at_exit():
    pass


def at_graceful_exit():
    pass


def at_interrupt():
    pass


def at_terminate():
    pass


def initialize(glob, sudo=False, multi_debug_level=False, add_help=True):
    """
    Initialization function ; sets up the arguments for the parser and creates a
     logger to be inserted in the input dictionary of global variables from the
     calling script.

    :param glob: globals() instance from the calling script
    :param sudo: if True, require sudo credentials and re-run script with sudo
    :param multi_debug_level: allow to use -v, -vv, -vvv (adjust logging level)
                               instead of just -v (only debug on/off)
    :param add_help: set add_help in ArgumentParser
    """
    global parser, __parsers
    # 1) if sudo required, restart the script
    if sudo:
        # if not root, restart the script in another process and jump to this
        if os.geteuid() != 0:
            python = [] if glob['__file__'].startswith("./") else ["python"]
            os.execvp("sudo", ["sudo"] + python + sys.argv)
    # 2) format help message's variables and create the real argument parser
    p = os.path.basename(glob['__file__'])
    pn, _ = os.path.splitext(p)
    e = None if '__examples__' not in glob or len(glob['__examples__']) == 0 \
        else glob['__examples__']
    e = "Usage examples:\n" + '\n'.join(["  python {0} {1}".format(p, x) \
        for x in e]) if e is not None else e
    glob['parser'] = argparse.ArgumentParser(prog=pn, epilog=e,
        description=__descr_format(glob), add_help=add_help,
        formatter_class=argparse.RawTextHelpFormatter,
        conflict_handler="resolve")
    # 3) populate the real parser
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
    # 4) configure logging and get the main logger
    if multi_debug_level:
        glob['args']._debug_level = [logging.ERROR, logging.WARNING,
            logging.INFO, logging.DEBUG][min(glob['args'].verbose, 3)]
    else:
        glob['args']._debug_level = [logging.INFO, logging.DEBUG] \
                                    [glob['args'].verbose]
    logger.handlers = []
    glob['logger'] = logger
    handler = logging.StreamHandler()
    formatter = logging.Formatter(glob['LOG_FORMAT'], glob['DATE_FORMAT'])
    handler.setFormatter(formatter)
    glob['logger'].addHandler(handler)
    glob['logger'].setLevel(glob['args']._debug_level)
    if colored_logs_present:
        coloredlogs.DEFAULT_LOG_FORMAT = glob['LOG_FORMAT']
        coloredlogs.DEFAULT_DATE_FORMAT = glob['DATE_FORMAT']
        coloredlogs.install(glob['args']._debug_level, logger=glob['logger'])
    # 5) finally, bind the global exit handler
    def __at_exit():
        if __hooks.state == "INTERRUPTED":
            glob['at_interrupt']()
        elif __hooks.state == "TERMINATED":
            glob['at_terminate']()
        else:
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
        assert re.match(r'^_?[a-zA-Z][a-zA-Z0-9_]*$', param) is not None, \
               "Illegal argument name"
        try:
            result = eval(condition.replace(" ? ", " glob['args'].{} "
                                                   .format(param)))
        except AssertionError as e:
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
