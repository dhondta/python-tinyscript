# -*- coding: UTF-8 -*-
"""Module for defining common functions for report elements.

"""
from os.path import exists, splitext
from six import string_types


__all__ = ["output", "string_types", "Element", "TEXT"]

TEXT = True


def output(f):
    """ This decorator allows to choose to return an output as text or to save
         it to a file. """
    def wrapper(self, *args, **kwargs):
        try:
            text = kwargs.get('text') or args[0]
        except IndexError:
            text = True
        r = f(self, *args, **kwargs)
        if text:
            return r
        elif r is not None and isinstance(r, string_types):
            filename = "{}.{}".format(self.filename, f.__name__)
            while exists(filename):
                name, ext = splitext(filename)
                try:
                    name, i = name.split('-')
                    i = int(i) + 1
                except ValueError:
                    i = 2
                filename = "{}-{}".format(name, i) + ext
            with open(filename, 'w') as out:
                out.write(r)
    return wrapper


class Element(object):
    """ This class is used to give a common type to report elements. """
    _style = {'size': 12, 'style': "normal", 'color': "black"}
    id = 0
    
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', "%s-0" % self.__class__.__name__.lower())
        for k, v in kwargs.items():
            if k not in ['color', 'size', 'style']:
                continue
            self._style[k] = v
        self.style = "font-size:%(size)spx;font-style:%(style)s;color:%(color)s;" % self._style
        self._newline = "\n"
    
    def _set_indent(self, indent):
        return ("", "") if indent is None else (indent * " ", "\n")
    
    @output
    def css(self, text=TEXT):
        return ""
    
    @output
    def csv(self, text=TEXT):
        return ""
    
    @output
    def html(self, indent=4, text=TEXT):
        return ""
    
    @output
    def json(self, text=TEXT):
        return {self.name: self.data}
    
    @output
    def md(self, text=TEXT):
        return ""
    
    @output
    def xml(self, indent=2, text=TEXT):
        return ("<%(name)s>{0}{1}{0}</%(name)s>" % self.__dict__).format(self._newline, str(self.data))

