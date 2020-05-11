#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining progress mode logic.

"""
from tqdm import tqdm, trange


__all__ = ["set_progress_items"]


def set_progress_items(glob):
    """
    This function prepares the progress items for inclusion in main script's global scope.
    
    :param glob: main script's global scope dictionary reference
    """
    a = glob['args']
    enabled = getattr(a, a._collisions.get("progress") or "progress", False)
    # Progress manager, for providing an interface to tqdm progress bar class
    class __ProgressManager(object):
        """ Simple progress bar manager, relying on tqdm module. """
        def __init__(self):
            c = a._collisions
            self._tqdm = None
        
        def __getattr__(self, name):
            if enabled:
                try:
                    return self.__getattribute__(name)
                except AttributeError:
                    pass
                if hasattr(tqdm, name) and self._tqdm is not None:
                    return getattr(self._tqdm, name)
                raise AttributeError("ProgressManager instance has no attribute '{}'".format(name))
        
        def range(self, *args, **kwargs):
            """ Dummy alias to trange. """
            if enabled:
                self._tqdm = trange(*args, **kwargs)
                return self._tqdm
        
        def start(self, *args, **kwargs):
            if enabled:
                self.stop()
                self._tqdm = tqdm(*args, **kwargs)
                return self._tqdm
        
        def stop(self):
            """ Closing method. """
            if enabled:
                if self._tqdm is not None:
                    self._tqdm.close()
                self._tqdm = None
    glob['progress_manager'] = manager = __ProgressManager()
    # shortcut function to range-based progress bar
    def progressbar(*args, **kwargs):
        """ Range-based progress bar relying on tqdm. """
        try:
            iter(args[0])
            return manager.start(*args, **kwargs)
        except TypeError as te:
            return manager.range(*args, **kwargs)
    glob['progressbar'] = progressbar
