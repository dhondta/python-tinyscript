# -*- coding: UTF-8 -*-
"""Module for enhancing logging preimport.

"""
import coloredlogs
import logging


def __set_logger(glob, *names):
    if len(names) == 0:
        names = [None]
    for name in names:
        logger = logging.getLogger(name)
        dl = glob['args']._debug_level
        for h in logger.handlers:
            h.setFormatter(logging.Formatter(glob['LOG_FORMAT'],
                                             glob['DATE_FORMAT']))
        logger.setLevel(dl)
        coloredlogs.install(dl,
                            logger=logger,
                            fmt=glob['LOG_FORMAT'],
                            datefmt=glob['DATE_FORMAT'], 
                            milliseconds=glob['TIME_MILLISECONDS'],
                            syslog=glob['args']._debug_syslog,
                            stream=glob['args']._debug_logfile)


logging.setLogger = __set_logger
