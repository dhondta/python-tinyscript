# -*- coding: UTF-8 -*-
"""Module for enhancing logging preimport.

"""
import coloredlogs
import logging
import re
import sys
import types
from functools import wraps
from platform import system
from time import gmtime

from .inspectp import inspect


PY3 = sys.version[0] == "3"
logging.START_TIME = None


# setup a null logger
logging.nullLogger = logging.getLogger("null")
logging.nullLogger.setLevel(1000)
logging.nullLogger.addHandler(logging.NullHandler())


def __del(d, k):
    try:
        if isinstance(d, dict):
            del d[k]
        else:
            delattr(d, str(k))
    except (AttributeError, KeyError):
        pass


def addLogLevel(levelName, color, level, bold=True):
    """ Add a new log level.
    
    :param levelName: name for the new level
    :param color:     related message color
    :param level:     integer defining the level
    :param bold:      whether the related messages should be displayed in bold
    """
    n, N = levelName, levelName.upper()
    if hasattr(logging, N):
        raise ValueError("Cannot overwrite log level '{}'".format(n))
    setattr(logging, N, level)
    setattr(logging, N + "_COLOR", color)
    logging.addLevelName(level, N)
    def display(self, message, *args, **kwargs):
        if self.isEnabledFor(level):
            self._log(level, message, args, **kwargs)
    display.__name__ = n
    setattr(logging.Logger, n, display)
    attrs = {'color': color}
    if bold:
        attrs['bold'] = system() != "Windows"
    coloredlogs.DEFAULT_LEVEL_STYLES[n] = attrs
    if PY3:
        logging._levelToName[level] = N
        logging._nameToLevel[N] = level
    else:
        logging._levelNames[level] = N
logging.addLogLevel = addLogLevel


def bindLogger(f):
    """ This decorators allows either to bind a logger to self if f is a method or to bind a logger in the local scope
         of f if it is a function. It tries first to get the logger from kwargs, or then tries to get the logger from
         caller's globals or finally sets a null logger. This way, the logger can be used inside the function without
         caring to get a logger itself.
    
    Inspired from: https://stackoverflow.com/questions/17862185/how-to-inject-variable-into-scope-with-a-decorator
    """
    @wraps(f)
    def _wrapper(*args, **kwargs):
        logger = kwargs.pop('logger', None) or f.__globals__.get('logger') or inspect.getmainglobals().get('logger') \
                 or logging.nullLogger
        if logger.name not in ["main", "null"]:
            setLogger(logger.name)
        # if f is a method, bind the logger to self
        if inspect.ismethod(f) or f.__code__.co_varnames[0] == "self":
            args[0].logger = logger
            return f(*args, **kwargs)
        # otherwise, pass the logger through globals
        else:
            glob = f.__globals__
            sentinel = object()
            old = glob.get('logger', sentinel)
            glob['logger'] = logger
            try:
                return f(*args, **kwargs)
            finally:
                if old is sentinel:
                    del glob['logger']
                else:
                    glob['logger'] = old
    return _wrapper
logging.bindLogger = bindLogger


def configLogger(logger, level="INFO", **kwargs):
    """ Configure colored logging for the given logger. """
    if kwargs.pop('relative', False):
        coloredlogs.ColoredFormatter = RelativeTimeColoredFormatter
    kwargs['fmt'] = kwargs.get('fmt', coloredlogs.DEFAULT_LOG_FORMAT)
    kwargs['datefmt'] = kwargs.get('datefmt', coloredlogs.DEFAULT_DATE_FORMAT)
    f = logging.Formatter(kwargs['fmt'], kwargs['datefmt'])
    level = level if isinstance(level, int) else getattr(logging, level)
    # ensure the InterceptionHandler is present
    if not any(isinstance(h, logging.InterceptionHandler) for h in logger.handlers):
        h = logging.InterceptionHandler()
        h.setLevel(1)
        logger.addHandler(h)
    # ensure there is at least one StreamHandler
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        h = logging.StreamHandler()
        h.setFormatter(f)
        h.setLevel(level)
        logger.addHandler(h)
        coloredlogs.install(level, logger=logger, **kwargs)
    # now, update logger's relevant handlers with the new level
    for h in logger.handlers:
        if not isinstance(h, logging.InterceptionHandler):
            h.setFormatter(f)
            h.setLevel(level)
            coloredlogs.install(level, logger=logger, **kwargs)
logging.configLogger = configLogger


def delLevelName(level):
    """ Remove association of 'levelName' with 'level'. """
    logging._acquireLock()
    if isinstance(level, int):
        levelName = logging._levelToName[level] if PY3 else logging._levelNames[level]
    else:
        levelName = level.upper()
        level = logging._nameToLevel.get(levelName) if PY3 else \
                {v: k for k, v in logging._levelNames.items()}.get(levelName)
    __del(getattr(logging, "_levelToName", None), level)
    __del(getattr(logging, "_levelNames", None), level)
    __del(getattr(logging, "_nameToLevel", None), levelName)
    logging._releaseLock()
logging.delLevelName = delLevelName


def delLogLevel(levelName):
    """ Remove a log level. """
    n, N = levelName, levelName.upper()
    if not hasattr(logging, N):
        raise ValueError("Log level '{}' does not exist".format(n))
    __del(logging, N)
    __del(globals(), "{}_COLOR".format(N))
    delLevelName(levelName)
    __del(logging.Logger, n)
    __del(coloredlogs.DEFAULT_LEVEL_STYLES, n)
logging.delLogLevel = delLogLevel


def lastLogRecord():
    """ Display the last log record. """
    rec = getattr(logging, "_last_record", None)
    if rec:
        lastrec = logging.getLogger("__last_record__")
        lastrec.name = rec.name
        lastrec.log(rec.levelno, rec.msg)
        lastrec.name = "__last_record__"
logging.lastLogRecord = lastLogRecord


def renameLogger(old_name, new_name):
    """ Rename a logger with a different name. It raises an exception if the new name exists in the native dictionary of
         loggers.
    
    :param old_name: old logger name
    :param new_name: new logger name
    """
    if old_name not in logging.root.manager.loggerDict.keys():
        raise ValueError("Logger name does not exist")
    if new_name in logging.root.manager.loggerDict.keys():
        raise ValueError("New logger name already exists")
    logger = logging.root.manager.loggerDict.pop(old_name)
    logger.name = new_name
    logging.root.manager.loggerDict[new_name] = logger
logging.renameLogger = renameLogger


def setLogger(name=None):
    """ Set up the logger with the given name according to Tinyscript's logging configuration.
    
    :param name: logger name
    """
    setLoggers(name)        
logging.setLogger = setLogger


def setLoggers(*names):
    """ Set up the loggers with the given names according to Tinyscript's logging configuration.
    
    :param names: logger names
    """
    if len(names) == 0:
        names = [None]
    main = inspect.getmainglobals().get('logger') or logging.getLogger()
    main.setLevel(1)
    if not any(type(h) is InterceptionHandler for h in main.handlers):
        main.addHandler(InterceptionHandler())
    # ensure that the main logger has no parent
    main.parent = None
    for name in names:
        logger = logging.getLogger(name)
        # check that the given logger is not Tinyscript's one
        if main.name == name or id(main) == id(logger):
            continue
        # set Tinyscript's logger as the logger's parent
        logger.parent = main
        # copy the reference to the list of handlers
        logger.handlers = main.handlers
        # disable propagation from the sublogger so that it does not duplicate log messages
        logger.propagate = False
logging.setLoggers = setLoggers


def setLoggingLevel(level="INFO", *patterns, **kwargs):
    """ Set logging level for loggers whose names match the list of patterns. """
    level = getattr(logging, level) if not isinstance(level, int) else level
    for l in list(logging.root.manager.loggerDict.keys()):
        if any(re.match(p, l) for p in patterns):
            l = logging.getLogger(l)
            l.setLevel(level)
            kwargs.get('config_func', logging.configLogger)(l, level)
logging.setLoggingLevel = setLoggingLevel


def unsetLogger(name, force=False):
    """ Remove a logger. If the name does not exist in the dictionary of loggers, it raises an exception.
    
    :param name: logger name
    """
    logger = logging.root.manager.loggerDict.get(name)
    if name is None or not isinstance(logger, logging.Logger):
        raise ValueError("Logger name does not exist")
    children = []
    for n, l in logging.root.manager.loggerDict.items():
        if n != name and isinstance(l, logging.Logger) and l.parent == logger:
            children.append(n)
    if len(children) > 0 and not force:
        raise ValueError("This logger is the parent of '{}'".format("', '".join(children)))
    for n in children:
        logging.getLogger(n).name = None
    logging.root.manager.loggerDict.pop(name)
logging.unsetLogger = unsetLogger


def unsetLoggers(*names, **kwargs):
    """ Remove loggers. If a name does not exist in the dictionary of loggers, it raises an exception.
    
    :param names: logger names
    """
    force = kwargs.get('force', False)
    for name in names:
        unsetLogger(name)
logging.unsetLoggers = unsetLoggers


class InterceptionHandler(logging.Handler):
    """ Dummy handler saving the last handled log record. """
    def __init__(self):
        super(InterceptionHandler, self).__init__(1)
    
    def handle(self, record):
        logging._last_record = record
logging.InterceptionHandler = InterceptionHandler


class RelativeTimeColoredFormatter(coloredlogs.ColoredFormatter):
    """ Custom formatter for computing relative times. """
    converter = gmtime
    
    def __init__(self, *args, **kwargs):
        super(RelativeTimeColoredFormatter, self).__init__(*args, **kwargs)
        self.datefmt = '%H:%M:%S.%f'
    
    def format(self, record):
        record.created = record.relativeCreated / 1000
        return super(RelativeTimeColoredFormatter, self).format(record)
logging.RelativeTimeColoredFormatter = RelativeTimeColoredFormatter


class Std2Logger:
    """ File-like stream object redirecting writes to a logger.
    
    Inspired from: https://stackoverflow.com/questions/11124093/redirect-python-print-output-to-logger/36296215
    """
    def __init__(self, logger, level="INFO"):
        level = getattr(logging, level) if not isinstance(level, int) else level
        self.__logger, self.__level, self.__buffer = logger, level, ""
    
    def write(self, data):
        data = self.__buffer + data
        self.__buffer = ""
        for line in data.splitlines(True):
            if line[-1] == "\n":
                self.__logger.log(self.__level, line.rstrip())
            else:
                self.__buffer += line
    
    def flush(self):
        if self.__buffer:
            self.__logger.log(self.__level, self.__buffer.rstrip())
        self.__buffer = ""
logging.Std2Logger = Std2Logger


# setup the private logger for displaying the last intercepted log record
def __setup_lr_logger():
    l = logging.getLogger("__last_record__")
    l.setLevel(1)
    h = logging.StreamHandler()
    f = logging.Formatter("\r%(asctime)s [%(levelname)s] %(message)s")
    h.setFormatter(f)
    l.addHandler(h)
    coloredlogs.install(1, logger=l)
__setup_lr_logger()

