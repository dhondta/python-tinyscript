#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining stepping mode logic.

"""
from .helpers.utils import std_input
from .loglib import STEP_COLOR


__all__ = ["set_step_items"]


def set_step_items(glob):
    """
    This function prepares the stepping items for inclusion in main script's
     global scope.
    
    :param glob: main script's global scope dictionary reference
    """
    try:
        enabled = glob['args'].step
    except AttributeError:
        enabled = False
    
    class Step(object):
        def __init__(self, message=None, at_end=False):
            self.message = message
            self.at_end = at_end
            
        def __enter__(self):
            if enabled:
                if self.message:
                    glob['logger'].step(self.message)
                if not self.at_end:
                    std_input("Press enter to continue", {'color': STEP_COLOR,
                                                          'bold': True})
        
        def __exit__(self, *args):
            if enabled and self.at_end:
                std_input("Press enter to continue", {'color': STEP_COLOR,
                                                      'bold': True})
    
    glob['Step'] = Step
    
    def step(message=None):
        if enabled:
            if message:
                glob['logger'].step(message)
            std_input("Press enter to continue", {'color': STEP_COLOR,
                                                  'bold': True})
    
    glob['step'] = step
