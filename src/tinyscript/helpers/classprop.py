# -*- coding: UTF-8 -*-
"""Class property.

"""
__all__ = __features__ = ["classproperty"]


def classproperty(f):
    if not isinstance(f, (classmethod, staticmethod)):
        f = classmethod(f)
    return ClassProperty(f)


# inspired from: https://stackoverflow.com/questions/5189699/how-to-make-a-class-property
class ClassProperty(object):
    """ ClassProperty class for implementing @classproperty. """
    def __init__(self, fget=None, fset=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.__doc__ = doc or getattr(fget, "__doc__", None)
    
    def __get__(self, obj, objtype=None):
        objtype = objtype or type(obj)
        return self.fget.__get__(obj, objtype)()
    
    def setter(self, f):
        if not isinstance(f, (classmethod, staticmethod)):
            f = classmethod(f)
        self.fset = f
        return self

