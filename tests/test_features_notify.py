#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Notification feature module assets' tests.

"""
from tinyscript import *
from tinyscript.features.notify import set_notify_items

from utils import *


NOTIFICATION_TIMEOUT = 1
NOTIFICATION_LEVEL   = 10  # logging.DEBUG


class TestNotify(TestCase):    
    @classmethod
    def setUpClass(cls):
        # collect ProxyArgumentParser object reference from the scope of tinyscript to reuse it afterwards (as it will
        #  be overwritten with the reference of a real parser each time initialize(...) is called)
        cls.argv = sys.argv[1:]  # backup input arguments
        sys.argv[1:] = ["--notify"]
        initialize()
    
    @classmethod
    def tearDownClass(cls):
        sys.argv[1:] = cls.argv  # restore input arguments
        for h in logger.handlers[:]:
            if h.__class__.__name__ == "NotificationHandler":
                logger.handlers.remove(h)
    
    def test_notify_setup(self):
        g = globals().keys()
        self.assertTrue(args.notify)
        self.assertIn("notify", g)
    
    def test_notifications(self):
        logger.info("test message")
        logger.warning("test message")
        logger.error("test message")
        g = globals()
        g['NOTIFICATION_TIMEOUT'] = "BAD"
        self.assertRaises(ValueError, set_notify_items, g)
        g['NOTIFICATION_TIMEOUT'] = 1
        g['NOTIFICATION_LEVEL']   = -1
        self.assertRaises(ValueError, set_notify_items, g)
        g['NOTIFICATION_LEVEL']   = 10
        g['NOTIFICATION_ICONS_PATH'] = "/path/does/not/exist"
        self.assertRaises(ValueError, set_notify_items, g)

