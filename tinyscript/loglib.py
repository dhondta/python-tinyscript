#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining logging-related constants and objects.

"""
import logging
# colorize logging
try:
    import coloredlogs
    colored_logs_present = True
except ImportError:
    print("(Install 'coloredlogs' for colored logging)")
    coloredlogs = None
    colored_logs_present = False

from .__info__ import __author__, __copyright__, __version__


__features__ = ["LOG_FORMAT", "DATE_FORMAT", "logger", "logging"]
__all__ = ["coloredlogs", "colored_logs_present", "configure_logger"] + \
          __features__


LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DATE_FORMAT = '%H:%M:%S'


# setup a default logger for allowing logging before initialize() is called
logger = logging.getLogger("main")
if colored_logs_present:
    coloredlogs.DEFAULT_LOG_FORMAT = LOG_FORMAT
    coloredlogs.DEFAULT_DATE_FORMAT = DATE_FORMAT
    coloredlogs.install(logger=logger)


def configure_logger(glob, multi_level):
    """
    Logger configuration function for setting either a simple debug mode or a
     multi-level one.
    
    :param glob:        globals dictionary
    :param multi_level: boolean telling if multi-level debug is to be considered
    """
    if multi_level:
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
