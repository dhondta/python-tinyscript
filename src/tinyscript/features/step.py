#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining stepping mode logic.

"""
from ..helpers.inputs import std_input
from ..preimports import logging


__all__ = ["set_step_items"]


COLOR = logging.STEP_COLOR


def set_step_items(glob):
    """ This function prepares the stepping items for inclusion in main script's global scope.
    
    :param glob: main script's global scope dictionary reference
    """
    a = glob['args']
    l = glob['logger']
    enabled = getattr(a, a._collisions.get("step") or "step", False)
    # Step context manager, for defining a block of code that can be paused at its start and end
    class Step(object):
        def __init__(self, message=None, at_end=False):
            self.message = message
            self.at_end = at_end
            
        def __enter__(self):
            if enabled:
                if self.message:
                    l.step(self.message)
                if not self.at_end:
                    std_input("Press enter to continue", ["bold", COLOR])
                return self
        
        def __exit__(self, *args):
            if enabled and self.at_end:
                std_input("Press enter to continue", ["bold", COLOR])
    glob['Step'] = Step
    # stepping function, for stopping the execution and displaying a message if any defined
    def step(message=None):
        if enabled:
            if message:
                l.step(message)
            std_input("Press enter to continue", ["bold", COLOR])
    glob['step'] = step

