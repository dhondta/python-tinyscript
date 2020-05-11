#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining logging-related constants and objects.

"""
import coloredlogs
from datetime import timedelta
from time import gmtime

from .preimports import logging


__features__ = ["LOG_FORMAT", "DATE_FORMAT", "TIME_MILLISECONDS", "logger"]
__all__      = ["coloredlogs", "configure_logger"] + __features__


DATE_FORMAT       = '%H:%M:%S'
LOG_FORMAT        = '%(asctime)s [%(levelname)s] %(message)s'
TIME_MILLISECONDS = False


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


class RelativeTimeColoredFormatter(coloredlogs.ColoredFormatter):
    """
    Custom formatter for computing relative times.
    """
    converter = gmtime
    
    def __init__(self, *args, **kwargs):
        super(RelativeTimeColoredFormatter, self).__init__(*args, **kwargs)
        self.datefmt = '%H:%M:%S.%f'
    
    def format(self, record):
        record.created = timedelta(microseconds=record.relativeCreated).total_seconds()
        return super(RelativeTimeColoredFormatter, self).format(record)


def configure_logger(glob, multi_level, relative=False, logfile=None, syslog=False):
    """
    Logger configuration function for setting either a simple debug mode or a multi-level one.
    
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
    logger.handlers = []
    logger.setLevel(1)
    logger.addHandler(_l.InterceptionHandler())
    handler = _l.StreamHandler()
    lfmt = "\r" + glob.get('LOG_FORMAT', LOG_FORMAT)
    dfmt = glob.get('DATE_FORMAT', DATE_FORMAT)
    formatter = _l.Formatter(lfmt, dfmt)
    handler.setFormatter(formatter)
    handler.setLevel(dl)
    logger.addHandler(handler)
    if relative:
        coloredlogs.ColoredFormatter = RelativeTimeColoredFormatter
    gtms = glob.get('TIME_MILLISECONDS', TIME_MILLISECONDS)
    coloredlogs.install(dl, logger=logger, fmt=lfmt, datefmt=dfmt, syslog=syslog, stream=logfile, milliseconds=gtms)
    lastrec = _l.getLogger("__last_record__")
    lastrec.handlers = []
    handler = _l.StreamHandler()
    handler.setFormatter(_l.Formatter("\r" + lfmt, dfmt))
    lastrec.addHandler(handler)
    lastrec.setLevel(1)
    coloredlogs.install(1, logger=lastrec, fmt="\r" + lfmt, datefmt=dfmt, milliseconds=gtms)
