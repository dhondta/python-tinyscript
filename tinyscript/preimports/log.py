# -*- coding: UTF-8 -*-
"""Module for enhancing logging preimport.

"""
import coloredlogs
import logging


def __set_loggers(glob, *names):
    """
    Set up the loggers with the given names according to Tinyscript's logging
     configuration.
    
    :param glob:  globals dictionary
    :param names: logger names
    """
    if len(names) == 0:
        names = [None]
    main = glob['logger']
    for name in names:
        logger = logging.getLogger(name)
        # check first that the given logger is not Tinyscript's one
        if main.name == name or id(main) == id(logger):
            continue
        # set Tinyscript's logger as the logger's parent
        logger.parent = main
        # copy the reference to the list of handlers
        logger.handlers = main.handlers
        # disable propagation from the sublogger so that it does not duplicate
        #  log messages
        logger.propagate = False
        # ensure that the main logger has no parent
        main.parent = None


logging.setLogger  = lambda g, n: __set_loggers(g, n)
logging.setLoggers = __set_loggers
