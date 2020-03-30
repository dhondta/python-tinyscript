# -*- coding: UTF-8 -*-
"""Common utility functions.

"""
import colorful
import os
import re
import sys
from six import StringIO

from .constants import *
from .data.types import is_function, is_lambda, is_str

# fix to Xlib.error.DisplayConnectionError: Can't connect to display ":0":
#  No protocol specified
if LINUX and os.geteuid() == 0:
    os.system("xhost +SI:localuser:root > /dev/null 2>&1")

from pynput.keyboard import Controller, Key, Listener


__all__ = __features__ = ["capture", "clear", "confirm", "handle_keystrokes",
                          "pause", "silent", "std_input", "stdin_pipe",
                          "user_input", "Capture"]

_keyboard = Controller()
pause = lambda *a, **kw: std_input("Press Enter to continue", *a, **kw) or None


def capture(f):
    """
    Decorator for capturing stdout and stderr.
    """
    def _wrapper(*a, **kw):
        with Capture() as (out, err):
            r = f(*a, **kw)
        return r, out.text, err.text
    return _wrapper


def clear():
    """
    Dummy multi-platform screen clear function.
    """
    from os import system
    if DARWIN or LINUX:
        system("clear")
    elif WINDOWS:
        system("cls")


def confirm(prompt="Are you sure ?", style="bold"):
    """
    Ask for confirmation.
    """
    return user_input(prompt, ["(Y)es", "(N)o"], "n", style=style) == "yes"


def handle_keystrokes(keystrokes, silent=True):
    """
    Keystrokes handling function relying on pynput.
    
    :param keystrokes: dictionary of keystrokes and related actions
    :param silent:     do not show errors (of keys not handled)
    
    Keystrokes dictionary formats:
    1. keystroke: on_press action
    2. keystroke: dictionary with on_press and on_release actions
    
    Action representations:
    1. (str, output handler)
    2. function returning None|str|(str, output handler)
    """
    for k, v in keystrokes.items():
        try:
            k_obj = getattr(Key, k)
            keystrokes[k_obj] = v
            del keystrokes[k]
        except Exception:
            pass
    
    def __handle(f):
        r = f()
        r, out = r if isinstance(r, tuple) and len(r) == 2 else (r, None)
        if is_str(r):
            if out is None:
                print(r)
            elif out in [sys.stdout, sys.stderr]:
                out.write(r)
                out.flush()
            else:
                out(r)
    
    def on_event(event):
        def _event_handler(key):
            k = str(key).strip("'")
            try:
                v = keystrokes[k]
                if isinstance(v, dict):
                    v = v.get(event)
                __handle(lambda: v if not is_function(v) else v)
            except KeyError:
                if not silent:
                    raise ValueError("Key '{}' not handled".format(k))
            except Exception:
                raise ValueError("Bad keystrokes handling")
        return _event_handler
    
    listener = Listener(on_press=on_event("on_press"),
                        on_release=on_event("on_release"))
    listener.start()
    listener.wait()
    return listener


def silent(f):
    """
    Decorator for silencing stdout and stderr.
    """
    def _wrapper(*a, **kw):
        with Capture():
            r = f(*a, **kw)
        return r
    return _wrapper


def std_input(prompt="", style=None, palette=None):
    """
    Very simple Python2/3-compatible input function handling prompt styling.
    
    :param prompt:  prompt message
    :param style:   colorful styling function, e.g. red_on_green (for green
                     foreground and red background colors)
    :param palette: dictionary for defining new styles
    """
    colorful.update_palette(palette or {})
    if style is not None:
        if isinstance(style, (list, tuple, set)):
            style = "_".join(style)
        prompt = getattr(colorful, style)(prompt)
    return (input(prompt) if PYTHON3 else raw_input(prompt)).strip()


def stdin_pipe():
    """
    Python2/3-compatible stdin pipe read function.
    """
    if PYTHON3:
        with open(0, 'rb') as f:
            for l in f:
                yield l
    else:
        for l in sys.stdin:
            yield l


def user_input(prompt="", choices=None, default=None, choices_str="",
               required=False, newline=False, **kwargs):
    """
    Python2/3-compatible input function handling choices and default value.
    
    :param prompt:      prompt message
    :param choices:     list of possible choices or lambda function
    :param default:     default value
    :param choices_str: list of possible choices as a string (overrides the
                         default composition from the list of choices)
    :param required:    make non-null user input mandatory
    :param newline:     insert a newline and '>>' after the prompt
    :param kwargs:      keyword-arguments to be passed to std_input for styling
    :return:            handled user input
    """
    shortcuts = {}
    if type(choices) in [list, tuple, set]:
        choices = list(map(lambda x: str(x).lower(), choices))
        choices_str = " {%s}" % (choices_str or \
                                 '|'.join(list(map(str, choices))))
        # consider choices of the form ["(Y)es", "(N)o"] ;
        #  in this case, we want the choices to be ['yes', 'no', 'y', 'n'] for
        #  the sake of simplicity for the user
        m = list(map(lambda x: re.match(r'\(([a-zA-Z0-9])\)', x), choices))
        # then remove the parenthesis from the choices
        choices = [re.sub(r"\(([a-zA-Z0-9])\)", 
                          lambda x: x.group(1).lower(), c) for c in choices]
        shortcuts = {x.group(1).lower(): c for x, c in zip(m, choices) \
                     if x is not None}
        # this way, if using ["Yes", "No"], choices will remain so
        _check = lambda v: str(v).lower() in choices or \
                           str(v).lower() in shortcuts.keys()
    elif is_lambda(choices):
        _check = choices
    else:
        _check = lambda v: True
    prompt += "{}{} ".format(choices_str, [" [{}]".format(default), ""] \
                                          [default is None and required])
    user_input, first = None, True
    while not user_input:
        user_input = std_input(["", prompt][first] + ["", "\n >> "][newline],
                               **kwargs)
        first = False
        if type(choices) in [list, tuple, set]:
            choices = list(map(lambda x: x.lower(), choices))
            user_input = user_input.lower()
        if user_input == "" and default is not None and _check(default):
            _ = str(default)
            return shortcuts.get(_) or _
        if user_input != "" and _check(user_input):
            _ = user_input
            return shortcuts.get(_) or _
        if not required:
            return


class _Text(object):
    """
    Dummy Text class for storing StringIO's content before closing it.
    """
    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.text


class Capture(object):
    """
    Context manager for capturing stdout and stderr.
    """
    def __init__(self, out=sys.stdout, err=sys.stderr):
        # backup original output file handles
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        
    def __enter__(self):
        # create new file handles
        sys.stdout, sys.stderr = StringIO(), StringIO()
        self.stdout, self.stderr = _Text(), _Text()
        # return references of the dummy objects
        return self.stdout, self.stderr
    
    def __exit__(self, *args):
        # freeze stdout and stderr contents before closing the file handles,
        #  using the references previously returned by __enter__
        self.stdout.text = sys.stdout.getvalue().strip() 
        self.stderr.text = sys.stderr.getvalue().strip()
        # close current file handles
        sys.stdout.close()
        sys.stderr.close()
        # restore original output file handles
        sys.stdout, sys.stderr = self._stdout, self._stderr
