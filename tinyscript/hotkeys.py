# -*- coding: UTF-8 -*-
"""Module for defining hotkeys.

"""
from os import getpid, kill
from signal import SIGINT, SIGTERM, SIGUSR1

from .handlers import _hooks
from .helpers.inputs import confirm, hotkeys, hotkeys_enabled
from .preimports import logging


__all__ = ["set_hotkeys"]


HOTKEYS = None


def __confirm_sig(prompt, sig):
    def _wrapper():
        kill(getpid(), SIGUSR1)
        if confirm(prompt):
            kill(getpid(), sig)
        _hooks.state = "RUNNING"
    return _wrapper


BASE_HOTKEYS = {
    'i': __confirm_sig("Do you really want to interrupt ?", SIGINT),
    'l': logging.lastLogRecord,
    'q': __confirm_sig("Do you really want to quit ?", SIGTERM),
}


def set_hotkeys(glob):
    """
    This function registers the hotkeys got from the global scope.
    
    :param glob: main script's global scope dictionary reference
    """
    if hotkeys_enabled:
        k = glob.get('HOTKEYS', HOTKEYS)
        # case 1: no hotkey to be configured
        if k is None:
            return
        # case 2: only the default hotkeys
        elif k == "default":
            return hotkeys(BASE_HOTKEYS)
        # case 3: only user-defined keys
        elif isinstance(k, dict):
            return hotkeys(k)
        # case 4: default hotkeys and user-defined keys mix
        elif isinstance(k, tuple) and len(k) == 2 and "default" in k:
            r = {}
            for hk in k:
                if hk == "default":
                    hk = BASE_HOTKEYS
                for key, actions in hk.items():
                    r[key] = actions
            return hotkeys(r)
        raise ValueError("Invalid HOTKEYS dictionary")
