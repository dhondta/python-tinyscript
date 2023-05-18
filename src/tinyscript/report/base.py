# -*- coding: UTF-8 -*-
"""Module for defining common functions for report elements.

"""

__all__ = ["output", "Element"]


def output(f):
    """ This decorator allows to choose to return an output as text or to save it to a file. """
    from functools import wraps
    f._output = True  # used in tinyscript.parser
    @wraps(f)
    def _wrapper(self, *args, **kwargs):
        from os.path import exists, splitext
        from six import string_types
        if 'text' in kwargs:
            raise DeprecationWarning("'text' keyword has been deprecated, please use 'save_to_file' instead")
        s2f = kwargs.pop('save_to_file', False)
        r = f(self, *args, **kwargs)
        if not s2f or r is None:
            return r
        if isinstance(r, dict):
            if f.__name__ == "json":
                from json import dumps
                r = dumps(r, indent=kwargs.get('indent', 2))
            elif f.__name__ == "yaml":
                from yaml import dump
                r = dump(r, indent=kwargs.get('indent', 2), width=kwargs.get('width', 0))
        if not isinstance(r, string_types):
            raise TypeError("got report data in an unknown format (%s) ; should be str" % type(r).__name__)
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
        from inspect import stack
        output_format = stack()[1][3]  # get the calling output format method name from the stack
        return Element.format_data(self._data, output_format)
    
    @data.setter
    def data(self, data):
        self._data = data
    
    @property
    def style(self):
        r = ""
        for s, k in zip(["font-size:%spx", "font-style:%s", "color:%s"], ['size', 'style', 'color']):
            if self._style.get(k):
                r += s % str(self._style[k]) + ";"
        return r
    
    @output
    def csv(self, sep=','):
        return ""
    
    @output
    def html(self, indent=4):
        return ""
    
    @output
    def json(self):
        return {self.name: self.data}
    
    @output
    def md(self):
        return ""
    rst = md
    
    @output
    def xml(self, indent=2):
        return ("<%(name)s>{0}{1}{0}</%(name)s>" % self.__dict__).format(self._newline, str(self.data))
    
    @output
    def yaml(self, indent=2):
        return self.json(indent=indent, save_to_file=False)
    
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

