#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining logging-related constants and objects.

"""
import coloredlogs
import logging
from datetime import timedelta
from time import gmtime

from .__info__ import __author__, __copyright__, __version__


__features__ = ["LOG_FORMAT", "DATE_FORMAT", "TIME_MILLISECONDS",
                "logger", "logging"]
__all__ = ["coloredlogs", "configure_logger"] + __features__


DATE_FORMAT       = '%H:%M:%S'
LOG_FORMAT        = '%(asctime)s [%(levelname)s] %(message)s'
TIME_MILLISECONDS = False


def create_log_level(name, color, level, bold=True):
    setattr(logging, name.upper(), level)
    globals()["{}_COLOR".format(name.upper())] = color
    logging.addLevelName(level, name.upper())
    def display(self, message, *args, **kwargs):
        if self.isEnabledFor(level):
            self._log(level, message, args, **kwargs)
    display.__name__ = name
    setattr(logging.Logger, name, display)
    attrs = {'color': color}
    if bold:
        attrs['bold'] = coloredlogs.CAN_USE_BOLD_FONT
    coloredlogs.DEFAULT_LEVEL_STYLES[name] = attrs


# add a custom log level for interactive mode
create_log_level("interact", "cyan", 100)
# add a custom log level for stepping
create_log_level("step", "cyan", 101)
# add a custom log level for timing
create_log_level("time", "magenta", 102)
# add a custom success log level
create_log_level("success", "green", 103)
# add a custom failure log level
create_log_level("failure", "red", 104)


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
    logger.handlers = []
    glob['logger'] = logger
    handler = logging.StreamHandler()
    formatter = logging.Formatter(glob['LOG_FORMAT'], glob['DATE_FORMAT'])
    handler.setFormatter(formatter)
    glob['logger'].addHandler(handler)
    glob['logger'].setLevel(dl)
    if relative:
        coloredlogs.ColoredFormatter = RelativeTimeColoredFormatter
    coloredlogs.install(dl,
                        logger=glob['logger'],
                        fmt=glob['LOG_FORMAT'],
                        datefmt=glob['DATE_FORMAT'], 
                        milliseconds=glob['TIME_MILLISECONDS'],
                        syslog=syslog,
                        stream=logfile)
