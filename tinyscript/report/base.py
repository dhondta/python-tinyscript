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
        _ = f(self, *args, **kwargs)
        if text:
            return _
        elif _ is not None and isinstance(_, string_types):
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
                out.write(_)
    return wrapper


class Element(object):
    """ This class is used to give a common type to report elements. """
    pass
