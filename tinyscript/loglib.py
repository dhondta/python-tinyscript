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
    colored_logs_present = False

from .__info__ import __author__, __copyright__, __version__


__features__ = ["LOG_FORMAT", "DATE_FORMAT", "logger", "logging"]
__all__ = ["coloredlogs", "colored_logs_present", "logging"] + __features__


LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DATE_FORMAT = '%H:%M:%S'


# setup a default logger for allowing logging before initialize() is called
logger = logging.getLogger("main")
if colored_logs_present:
    coloredlogs.DEFAULT_LOG_FORMAT = LOG_FORMAT
    coloredlogs.DEFAULT_DATE_FORMAT = DATE_FORMAT
    coloredlogs.install(logger=logger)
