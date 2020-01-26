#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining logging-related constants and objects.

"""
import coloredlogs
from datetime import timedelta
from time import gmtime

from .preimports import logging


__features__ = ["LOG_FORMAT", "DATE_FORMAT", "TIME_MILLISECONDS", "logger"]
__all__ = ["coloredlogs", "configure_logger"] + __features__


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
        record.created = timedelta(microseconds=record.relativeCreated) \
                         .total_seconds()
        return super(RelativeTimeColoredFormatter, self).format(record)


def configure_logger(glob, multi_level,
                     relative=False, logfile=None, syslog=False):
    """
    Logger configuration function for setting either a simple debug mode or a
     multi-level one.
    
    :param glob:        globals dictionary
    :param multi_level: boolean telling if multi-level debug is to be considered
    :param relative:    use relative time for the logging messages
    :param logfile:     log file to be saved (None means do not log to file)
    :param syslog:      enable logging to /var/log/syslog
    """
    levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG] \
             if multi_level else [logging.INFO, logging.DEBUG]
    try:
        verbose = min(int(glob['args'].verbose), 3)
    except AttributeError:
        verbose = 0
    glob['args']._debug_level = dl = levels[verbose]
    glob['args']._debug_syslog = syslog
    glob['args']._debug_logfile = logfile
    logger.handlers = []
    glob['logger'] = logger
    handler = logging.StreamHandler()
    lfmt = glob.get('LOG_FORMAT', LOG_FORMAT)
    dfmt = glob.get('DATE_FORMAT', DATE_FORMAT)
    formatter = logging.Formatter(lfmt, dfmt)
    handler.setFormatter(formatter)
    glob['logger'].addHandler(handler)
    glob['logger'].setLevel(dl)
    if relative:
        coloredlogs.ColoredFormatter = RelativeTimeColoredFormatter
    coloredlogs.install(
        dl, logger=glob['logger'], fmt=lfmt, datefmt=dfmt,
        milliseconds=glob.get('TIME_MILLISECONDS', TIME_MILLISECONDS),
        syslog=syslog, stream=logfile,
    )
