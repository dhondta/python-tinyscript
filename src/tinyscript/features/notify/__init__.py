#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining the notify feature.

"""
from os.path import dirname, isfile, join

from ...helpers.notify import notify
from ...helpers.constants import LINUX
from ...helpers.data.types import folder_exists, positive_int
from ...preimports import logging


__all__ = ["set_notify_items"]


def set_notify_items(glob):
    """
    This function prepares the notify items for inclusion in main script's global scope.
    
    :param glob: main script's global scope dictionary reference
    """
    a = glob['args']
    enabled = getattr(a, a._collisions.get("notify") or "notify", False)
    appname = glob.get('__scriptname__')
    timeout = positive_int(glob.get('NOTIFICATION_TIMEOUT', 5), zero=False)
    icon_path = folder_exists(glob.get('NOTIFICATION_ICONS_PATH', dirname(__file__)))
    level = positive_int(glob.get('NOTIFICATION_LEVEL', logging.SUCCESS))
    
    class NotificationHandler(logging.Handler):
        def emit(self, record):
            title = "{}[{}]:".format(appname, record.name) if record.name != "main" else appname
            icon = record.levelname.lower()
            ipath = join(icon_path, icon) + ".png"
            if isfile(ipath):
                icon = ipath
            notify(title, record.msg, appname, icon, timeout, title + " " + record.levelname)
    
    if enabled and not any(type(h) is NotificationHandler for h in glob['logger'].handlers):
        nh = NotificationHandler()
        nh.setLevel(level)
        glob['logger'].addHandler(nh)
    glob['notify'] = notify

