# -*- coding: UTF-8 -*-
"""Module for defining common functions for report elements.

"""
from functools import wraps
from inspect import stack
from os.path import exists, splitext
from six import string_types


__all__ = ["output", "string_types", "Element", "TEXT"]

TEXT = True


def output(f):
    """ This decorator allows to choose to return an output as text or to save
         it to a file. """
    f._output = True
    @wraps(f)
    def _wrapper(self, *args, **kwargs):
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
    return _wrapper


class Element(object):
    """ This class is used to give a common type to report elements. """
    _style = {}
    id = 0
    
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', self.__class__.__name__.lower())
        self.css = ""
        for k, v in kwargs.items():
            if k in ['color', 'size', 'style']:
                self._style[k] = v
        self._newline = "\n"
    
    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.name)
    
    def _set_indent(self, indent):
        return ("", "") if indent is None else (indent * " ", "\n")
    
    @property
    def data(self):
        output_format = stack()[1][3]  # get the calling output format method name from the stack
        return Element.format_data(self._data, output_format)
    
    @property
    def style(self):
        r = ""
        for s, k in zip(["font-size:%spx", "font-style:%s", "color:%s"], ['size', 'style', 'color']):
            if self._style.get(k):
                r += s % str(self._style[k]) + ";"
        return r
    
    @data.setter
    def data(self, data):
        self._data = data
    
    @output
    def csv(self, sep=',', text=TEXT):
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
    rst = md
    
    @output
    def xml(self, indent=2, text=TEXT):
        return ("<%(name)s>{0}{1}{0}</%(name)s>" % self.__dict__).format(self._newline, str(self.data))
    
    @staticmethod
    def format_data(data, fmt):
        if isinstance(data, Element):
            return getattr(data, fmt, lambda: str(data))()
        if isinstance(data, (list, set, tuple)):
            t = type(data)
            data = list(data)
            for i, subdata in enumerate(data):
                data[i] = Element.format_data(subdata, fmt)
            data = t(data)
        elif isinstance(data, dict):
            for k, subdata in data.items():
                data[k] = Element.format_data(subdata, fmt)
        return data

