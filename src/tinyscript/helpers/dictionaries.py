# -*- coding: UTF-8 -*-
"""Extra dictionary-based data structures.

"""
from time import time
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

from .data.types import is_class, is_list, is_str
from .path import Path
from ..preimports import re


__all__ = __features__ = ["flatten_dict", "merge_dict", "ClassRegistry", "ExpiringDict", "PathBasedDict"]


def flatten_dict(d, parent_key="", sep="/"):
    """ Flatten a dictionary of dictionaries.
    See: https://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def merge_dict(*dictionaries, **kwargs):
    """ Merge dictionaries into the first given one, that is, merging child dictionaries and lists.
    
    :param new:        create a new dictionary object or use first input's reference as the return value
    :param update:     update with the latest encountered value
    :param duplicates: keep duplicates in lists and tuples
    """
    new = kwargs.get('new', False)
    update = kwargs.get('update', True)
    duplicates = kwargs.get('duplicates', False)
    d = {} if new else dictionaries[0]
    for dictionary in dictionaries[int(not new):]:
        for k, v in dictionary.items():
            if k not in d:
                d[k] = v
            elif not update:
                continue
            elif isinstance(v, dict):
                d[k] = merge_dict(d[k], v, **kwargs)
            elif isinstance(v, (tuple, list)):
                l = list(d[k])
                for x in v:
                    if x in l and duplicates or x not in l:
                        l.append(x)
                if isinstance(v, tuple):
                    l = tuple(l)
                d[k] = l
            elif isinstance(v, set):
                for x in v:
                    d[k].add(x)
            else:
                d[k] = v
    return d


class ClassRegistry(dict):
    """ Custom dictionary class using class-based keys and list of subclass values.
    
    Example:
    >>> d = ts.ClassRegistry()
    >>> class Base: pass
    >>> class Sub1: pass
    >>> class Sub2: pass
    >>> d[Base] = Sub2
    >>> d["base", "sub1"]
    Traceback (most recent call last):
      File "<pyshell#120>", line 1, in <module>
        d["base", "sub1"]
      File "/mnt/data/Projects/maint/python-tinyscript/tinyscript/helpers/dictionaries.py", line 98, in __getitem__
        raise ValueError(subcls)
    ValueError: sub1
    >>> d["base", "sub2"]
    <class '__main__.Sub2'>
    >>> d["base"]
    <class '__main__.Base'>
    >>> d[Base]
    [<class '__main__.Sub2'>]
    """
    def __iter__(self):
        """ Iter over subclasses of every registered class. """
        for l in self.values():
            for subcls in l:
                yield subcls
    
    def __delitem__(self, key):
        """ Override the default __delitem__ method to handle class-keys and lists of subclasses. """
        if is_str(key):
            key = self[key]
        # remove a specific subclass
        elif is_list(key) and len(key) == 2:
            cls, subcls = key
            if is_class(subcls):
                subcls = subcls.__name__
            self[cls, subcls]
            if cls and not is_class(cls):
                cls = self[cls]
            found = False
            for k in (self.keys() if cls is None else [cls]):
                l = self[k]
                for v in l:
                    if is_class(v) and v.__name__.lower() == subcls.lower():
                        l.remove(v)
                        found = True
            if found:
                return
        super(ClassRegistry, self).__delitem__(key)
    
    def __getitem__(self, key):
        """ Override the default __getitem__ method to handle class-keys and lists of subclasses. """
        if key is None:
            return
        # get a class from its name
        if is_str(key):
            for k in self.keys():
                if is_class(k) and k.__name__.lower() == key.lower():
                    return k
        # get the list of subclasses associated to a class from its definition
        elif is_class(key):
            for k, v in self.items():
                if key is k:
                    return v
        # get subclass(es) from its parent class definition and its name
        elif is_list(key) and len(key) == 2:
            cls, subcls = key
            if is_class(subcls):
                return subcls
            if cls and not is_class(cls):
                cls = self[cls]
            l = []
            for k in (self.keys() if cls is None else [cls]):
                for v in self[k]:
                    if is_class(v) and v.__name__.lower() == subcls.lower():
                        l.append(v)
            if len(l) == 1:
                return l[0]
            elif len(l) > 1:
                return l
            else:
                raise ValueError(subcls)
        return super(ClassRegistry, self).__getitem__(key)
    
    def __setitem__(self, cls, subcls):
        """ Overwrite the default __setitem__ method to handle class-keys and lists of subclasses. """
        self.setdefault(cls, [])
        if subcls not in self[cls]:
            self[cls].append(subcls)


def _sort_by_text(text):
    """ Sorting function for considering strings with numbers (e.g. test1, test10, test100) """
    if isinstance(text, tuple):
        text, _ = text
    tokens = []
    for s in re.split(r"(\d+|\D+)", text):
        if s == "":
            continue
        tokens.append((int(s), len(s) - len(s.lstrip("0"))) if s.isdigit() else s)
    return tokens


class ExpiringDict(dict):
    """ Dictionary class with expiring keys, keeping these in chronological order (regarding arrival or refresh if
         enabled). """
    def __init__(self, items=None, max_age=0, sort_by_time=True, **kwargs):
        self.__expired = []
        self.__locked = False
        self.__times = {}
        self.max_age = max_age
        self.sort_by_time = sort_by_time
        if isinstance(items, dict):
            for k, v in sorted(items.items(), key=lambda x: x[0]):
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v
    
    def __check_expiration(self, key):
        """ Chck for key times and remove expired keys. """
        t = self.__times.get(key)
        if self.max_age > 0 and t is not None and time() - t > self.max_age:
            del self[key]
            self.__expired.append(key)
            return True
        return False
    
    def __cleanitems__(self):
        """ Clean expired items if the dictionary is unlocked. """
        if self.__locked:
            return
        # remove heading expired items
        for key in list(self.keys()):
            if not self.__check_expiration(key):
                break
    
    def __delitem__(self, key):
        """ Delete a key and its creation time. """
        super(ExpiringDict, self).__delitem__(key)
        del self.__times[key]
    
    def __getattribute__(self, name):
        """ Overridden method for applying key expiration for some requested attributes. """
        prefix = "_ExpiringDict__"
        if not name.startswith(prefix) and not self.__locked and not getattr(self, prefix + "cleaned", False):
            self.__cleaned = True
            self.__cleanitems__()
            self.__cleaned = False
        return super(ExpiringDict, self).__getattribute__(name)
    
    def __getitem__(self, key):
        """ Get a key, first updating expired keys, throwing a KeyExpiredError if the requested key is expired. """
        self.__cleanitems__()
        if key in self.__expired:
            self.__expired.remove(key)
            g = {'__name__': "__main__"}
            exec("class KeyExpiredError(ValueError): pass", g)
            raise g['KeyExpiredError'](key)
        return super(ExpiringDict, self).__getitem__(key)
    
    def __iter__(self):
        """ Override the normal __iter__, sorting by key in alphabetical order. """
        if self.sort_by_time:
            for k, _ in sorted(list(self.__times.items()), key=lambda x: x[1]):
                yield k
        else:
            for k in sorted(list(self.keys()), key=_sort_by_text):
                yield k
    
    def __setitem__(self, key, value):
        """ Set a key-value pair and its creation time. """
        # keep new keys at the tail of the dictionary
        if self.get(key) is not None:
            del self[key]
        if key in self.__expired:
            self.__expired.remove(key)
        super(ExpiringDict, self).__setitem__(key, value)
        self.__times[key] = time()
    
    def __str__(self):
        return str(dict(**self))
    
    def items(self):
        """ Override the normal items method, sorting the items by key in alphabetical order. """
        if self.sort_by_time:
            for k, _ in sorted(list(self.__times.items()), key=lambda x: x[1]):
                yield k, self[k]
        else:
            for k, v in sorted(list(super(ExpiringDict, self).items()), key=_sort_by_text):
                yield k, v
    
    def lock(self):
        """ Disable key expiration. """
        self.__locked = True
    
    def unlock(self):
        """ Re-enable key expiration. """
        self.__locked = False


class PathBasedDict(dict):
    """ Enhanced dictionary class handling keys as paths. """
    def __convert_path(self, path):
        """ Handle multiple path formats, e.g.:
            - "a/b/c/d"     (string)
            - Path("a/b/c/d")     (Path)
            - "a", "b", "c" (tuple of strings) """
        if not isinstance(path, tuple):
            path = (str(path),)
        path = tuple(filter(lambda x: x is not None, path))
        return Path(*path).parts
    
    def __delitem__(self, path):
        """ Remove the item at the given path of subdictionaries. """
        self[path]
        d, parts = self, self.__convert_path(path)
        if len(parts) > 1:
            del self[parts[:-1]][parts[-1]]
            parts = parts[:-1]
        while len(parts) > 1 and len(d[parts]) == 0:
            del self[parts[:-1]][parts[-1]]
            parts = parts[:-1]
        if len(parts) == 1 and (not isinstance(d[parts], dict) or len(d[parts]) == 0):
            super(PathBasedDict, self).__delitem__(parts[0])
    
    def __getitem__(self, path):
        """ Get the item from the given path of subdictionaries. """
        d, parts = self, self.__convert_path(path)
        try:
            for p in parts:
                d = d.get(p)
            if d is None:
                raise AttributeError
            return d
        except AttributeError:
            raise KeyError(parts)
    
    def __setitem__(self, path, value):
        """ Set the value to the given path of subdictionaries. """
        d, parts, curr = self, self.__convert_path(path), []
        if len(parts) > 1:
            for i, p in enumerate(parts[:-1]):
                d.setdefault(p, {})
                d = d[p]
                curr.append(p)
                if isinstance(d, PathBasedDict):
                    d[parts[i+1:]] = value
                    return
        if not isinstance(d, dict):
            raise ValueError("Path at '{}' already owns a value".format(str(Path(*curr))))
        if isinstance(d, PathBasedDict):
            super(PathBasedDict, d).__setitem__(parts[-1], value)
        else:
            d[parts[-1]] = value
    
    def count(self, path="", **kwargs):
        """ Count the number of values (given the attributes matching kwargs if any) under the given path of keys. """
        def _rcount(d=self, a=0):
            if isinstance(d, dict):
                for k, v in d.items():
                    a += _rcount(v)
            else:
                # when not a dict, we are at a leaf of the object tree, kwargs is then used as a set of criteria to be
                #  matched to include the object in the count
                a += [0, 1][len(kwargs) == 0 or all(getattr(d, attr, value) == value for attr, value in kwargs.items())]
            return a
        return _rcount(self[path])

