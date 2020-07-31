# -*- coding: UTF-8 -*-
"""Common utility functions.

"""
import colorful
import os
import re
import signal
import sys
from ast import literal_eval
from colorful.core import COLOR_PALETTE
from six import StringIO

from .compat import ensure_str
from .constants import *
from .data.types import is_function, is_lambda, is_str

# fix to Xlib.error.DisplayConnectionError: Can't connect to display ":0": No protocol specified
# however, it does not fix the error while testing with Travis CI
if LINUX:
    os.system("xhost +SI:localuser:{} > /dev/null 2>&1".format(USER))
os.environ['DISPLAY'] = os.environ.get('DISPLAY') or os.environ.get('REMOTE_DISPLAY', ":0")

try:
    from pynput.keyboard import Controller, Key, Listener
    _keyboard = Controller()
    hotkeys_enabled = True
except Exception:  # catch ImportError but also Xlib.error.DisplayConnectionError
    _keyboard = None
    hotkeys_enabled = False


__all__ = ["capture", "clear", "confirm", "hotkeys", "pause", "silent", "std_input", "stdin_flush", "stdin_pipe",
           "user_input", "Capture"]
__features__ = [x for x in __all__]
__all__ += ["colored"]

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


def colored(text, color=None, on_color=None, attrs=None, style=None, palette=None):
    """
    Colorize text.
    
    :param text:     text to be colorized
    :param color:    text color
    :param on_color: background color
    :param attrs:    single styling attribute or list of styling attributes
    :param style:    colorful styling function, e.g. red_on_green (for green foreground and red background colors)
    :param palette:  predefined palette's name (e.g. 'monokai')
    :return:         styled string
    
    Available styling attributes:
      blinkrapid, blinkslow, bold, concealed, dimmed, inversed, italic, reset, struckthrough, underlined
    
    Available palettes:
      monokai, solarized
    """
    if isinstance(style, (list, tuple)):
        style = "_".join(style)
    s = style or ""
    if palette:
        colorful.use_style(palette)
    if s == "":
        if attrs:
            if not isinstance(attrs, list):
                attrs = [attrs]
            for attr in attrs:
                if attr not in colorful.ansi.MODIFIERS.keys():
                    raise ValueError("Bad ANSI modifier '%s'" % attr)
                s += str(attr) + "_"
        if color:
            if color not in colorful.colorpalette.keys():
                raise ValueError("Bad color '%s'" % color)
            s += str(color) + "_"
        if on_color:
            if on_color not in colorful.colorpalette.keys():
                raise ValueError("Bad color '%s'" % on_color)
            s += "on_" + str(on_color)
    if s != "":
        c = getattr(colorful, s.rstrip("_"))
    try:
        return c(text).styled_string if s and TTY else text
    finally:
        # ensure that the palette is restored
        colorful.use_palette(COLOR_PALETTE)


def confirm(prompt="Are you sure ?", style="bold"):
    """
    Ask for confirmation.
    """
    return user_input("\r" + prompt, ["(Y)es", "(N)o"], "n", style=style) == "yes"


def hotkeys(hotkeys, silent=True):
    """
    Hotkeys declaration function relying on pynput.
    
    :param hotkeys: dictionary of hotkeys and related actions
    :param silent:  do not show errors (of keys not handled)
    :param die:     whether the hotkey should have its listener respawn or not
    
    Hotkeys dictionary formats:
    1. hotkey: on_press action
    2. hotkey: dictionary with on_press and on_release actions
    
    Action representations:
    1. (str, output handler)
    2. function returning None|str|(str, output handler)
    """
    if not hotkeys_enabled:
        return
    global listener, on_press
    # close the running listener, if hotkeys(...) was already called
    try:
        listener.stop()
        del listener
    except NameError:
        pass
    # replace string keys to Key.[...] objects (e.g. 'ctrl')
    for k, v in hotkeys.items():
        try:
            k_obj = getattr(Key, k)
            hotkeys[k_obj] = v
            del hotkeys[k]
        except Exception:
            pass
    
    def __handle(f):
        """ Hotkey action handler and listener regenerator. """
        global listener, on_press
        # stop the listener to avoid capturing multiple keystrokes
        listener.stop()
        # flush stdin to avoid printing the keystrokes
        stdin_flush()
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
        # open a new listener
        listener = Listener(on_press=on_press)
        listener.start()
    
    def on_press(key):
        """ Generic on_press callback function. """
        try:
            k = key._name_
        except AttributeError:
            k = key.char
        try:
            v = hotkeys[ensure_str(k)]
        except KeyError:
            if not silent:
                raise ValueError("Key '{}' not handled".format(k))
            return
        __handle((lambda: v) if not is_function(v) else v)
    
    listener = Listener(on_press=on_press)
    listener.start()


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
    :param style:   colorful styling function, e.g. red_on_green (for green foreground and red background colors)
    :param palette: dictionary for defining new styles
    """
    if style is not None:
        colorful.update_palette(palette or {})
        if isinstance(style, (list, tuple, set)):
            style = "_".join(style)
        prompt = colored(prompt, style=style)
    return (input(prompt) if PYTHON3 else raw_input(prompt)).strip()


def stdin_flush():
    """
    Multi-platform stdin flush function.
    
    Source: https://rosettacode.org/wiki/Keyboard_input/Flush_the_keyboard_buffer#Python
    """
    try:
        try:  # Windows
            from msvcrt import getch, kbhit
            while kbhit(): getch()
        except ImportError:  # Linux/Unix
            from termios import tcflush, TCIOFLUSH
            tcflush(sys.stdin, TCIOFLUSH)
    except Exception:
        pass


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


def user_input(prompt="", choices=None, default=None, choices_str="", required=False, newline=False, **kwargs):
    """
    Python2/3-compatible input function handling choices and default value.
    
    :param prompt:      prompt message
    :param choices:     list of possible choices or lambda function
    :param default:     default value
    :param choices_str: list of possible choices as a string (overrides the default composition from the choices list)
    :param required:    make non-null user input mandatory
    :param newline:     insert a newline and '>>' after the prompt
    :param kwargs:      keyword-arguments to be passed to std_input for styling
    :return:            handled user input
    """
    shortcuts = {}
    if type(choices) in [list, tuple, set]:
        choices = list(map(lambda x: str(x).lower(), choices))
        choices_str = " {%s}" % (choices_str or '|'.join(list(map(str, choices))))
        # consider choices of the form ["(Y)es", "(N)o"] ; in this case, we want the choices to be
        #  ['yes', 'no', 'y', 'n'] for the sake of simplicity for the user
        m = list(map(lambda x: re.match(r'\(([a-zA-Z0-9])\)', x), choices))
        # then remove the parenthesis from the choices
        choices = [re.sub(r"\(([a-zA-Z0-9])\)", lambda x: x.group(1).lower(), c) for c in choices]
        shortcuts = {x.group(1).lower(): c for x, c in zip(m, choices) if x is not None}
        # this way, if using ["Yes", "No"], choices will remain so
        _check = lambda v: str(v).lower() in choices or str(v).lower() in shortcuts.keys()
    elif is_lambda(choices):
        _check = choices
    else:
        _check = lambda v: True
    prompt += "{}{} ".format(choices_str, [" [{}]".format(default), ""][default is None and required])
    user_input, first = None, True
    while not user_input:
        stdin_flush()
        user_input = std_input(["", prompt][first] + ["", "\n >> "][newline], **kwargs)
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
        # freeze stdout and stderr contents before closing the file handles, using the references set in __enter__
        self.stdout.text = sys.stdout.getvalue().strip() 
        self.stderr.text = sys.stderr.getvalue().strip()
        # close current file handles
        sys.stdout.close()
        sys.stderr.close()
        # restore original output file handles
        sys.stdout, sys.stderr = self._stdout, self._stderr

