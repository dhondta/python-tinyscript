#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining logging-related constants and objects.

"""
import coloredlogs

from ..preimports import logging


__features__ = ["LOG_FORMAT", "DATE_FORMAT", "TIME_MILLISECONDS", "logger"]
__all__      = ["coloredlogs", "configure_logger"] + __features__


DATE_FORMAT       = '%H:%M:%S'
LOG_FORMAT        = '%(asctime)s [%(levelname)s] %(message)s'
TIME_MILLISECONDS = False


# add a custom level beneath DEBUG
logging.addLogLevel("detail", "green", 5, False)
# add a custom log level for interactive mode
logging.addLogLevel("interact", "cyan", 100)
# add a custom log level for stepping
logging.addLogLevel("step", "cyan", 101)
# add a custom log level for timing
logging.addLogLevel("time", "magenta", 102)
# add a custom success log level
logging.addLogLevel("success", "green", 103)
# add a custom failure log level
logging.addLogLevel("failure", "red", 104)


# setup a default logger for allowing logging before initialize() is called
logger = logging.getLogger("main")
logger.setLevel(1)
logger.addHandler(logging.InterceptionHandler())
coloredlogs.DEFAULT_LOG_FORMAT = LOG_FORMAT
coloredlogs.DEFAULT_DATE_FORMAT = DATE_FORMAT
coloredlogs.install(logger=logger)


def configure_logger(glob, multi_level, relative=False, logfile=None, syslog=False):
    """ Logger configuration function for setting either a simple debug mode or a multi-level one.
    
    :param glob:        globals dictionary
    :param multi_level: boolean telling if multi-level debug is to be considered
    :param relative:    use relative time for the logging messages
    :param logfile:     log file to be saved (None means do not log to file)
    :param syslog:      enable logging to /var/log/syslog
    """
    _l = logging
    levels = [_l.ERROR, _l.WARNING, _l.INFO, _l.DEBUG] if multi_level else [_l.INFO, _l.DEBUG]
    try:
        verbose = min(int(glob['args'].verbose), 3)
    except AttributeError:
        verbose = 0
    glob['args']._debug_level = dl = levels[verbose]
    glob['args']._debug_syslog = syslog
    glob['args']._debug_logfile = logfile
    glob['logger'] = logger
    # create the "last record" logger, used for reminding the last log record, i.e. with a shortcut key
    lastrec = logging.getLogger("__last_record__")
    kw = {'fmt': "\r" + glob.pop('LOG_FORMAT', LOG_FORMAT), 'datefmt': glob.pop('DATE_FORMAT', DATE_FORMAT)}
    if len(lastrec.handlers) != 1:
        for h in lastrec.handlers:
            lastrec.removeHandler(h)
        h = logging.StreamHandler()
        lastrec.addHandler(h)
    else:
        h = lastrec.handlers[0]
    h.setFormatter(logging.Formatter(*kw.values()))
    lastrec.setLevel(1)
    coloredlogs.install(1, logger=lastrec, **kw)
    logging.configLogger(logger, dl, syslog=syslog, stream=logfile, relative=relative,
                         milliseconds=glob.get('TIME_MILLISECONDS', TIME_MILLISECONDS), **kw)

