# -*- coding: UTF-8 -*-
"""Files/Folders-related checking functions and argument types.

"""
from os import environ
from os.path import sep

from .strings import _str2list
from ...constants import WINDOWS
from ...common import lazy_load_module
from ....preimports import os, re

lazy_load_module("magic")


__all__ = __features__ = []


# dummy shortcuts, compliant with the is_* naming convention
__all__ += ["is_dir", "is_executable", "is_file", "is_filemode", "is_filetype", "is_folder", "is_in_path",
            "is_mimetype"]
is_dir = is_folder = os.path.isdir
is_executable = lambda f: os.access(f, os.X_OK)
is_file = os.path.isfile
is_filemode = lambda m: len(m) == 3 and all(int(g) in range(8) for g in m)
is_filetype = lambda f, t: is_file(f) and re.search(t, magic.from_file(f)) is not None
is_in_path = lambda p: p in [x.rstrip(sep) for x in environ['PATH'].split(":;"[WINDOWS])]
is_mimetype = lambda f, m: is_file(f) and re.search(m, magic.from_file(f, mime=True)) is not None


# file and folder-related argument types
__all__ += ["file_does_not_exist", "file_exists", "file_mode", "file_mimetype", "file_type", "files_list",
            "files_mimetype", "files_type", "files_filtered_list", "folder_does_not_exist", "folder_exists",
            "folder_exists_or_create"]


def file_does_not_exist(f):
    """ Check that the given file does not exist. """
    if os.path.exists(f):
        raise ValueError("'{}' already exists".format(f))
    return f
folder_does_not_exist = file_does_not_exist
folder_does_not_exist.__name__ = "non-existing folder"
file_does_not_exist.__name__ = "non-existing file"


def file_exists(f):
    """ Check that the given file exists. """
    if not os.path.exists(f):
        raise ValueError("'{}' does not exist".format(f))
    if not os.path.isfile(f):
        raise ValueError("Target exists and is not a file")
    return f
file_exists.__name__ = "existing file"


def __file_type(mime=False):
    """ Check that the given file has the given {} type. """
    def _wrapper(ftype):
        def _subwrapper(f):
            if file_exists(f) and not [is_filetype, is_mimetype][mime](f, ftype):
                raise ValueError("Target's type is not {}".format(ftype))
            return f
        return _subwrapper
    _wrapper.__name__ = "MIME type"
    return _wrapper
file_mimetype, file_type = __file_type(True), __file_type()
file_mimetype.__doc__ = __file_type.__doc__.format("MIME")
file_type.__doc__ = __file_type.__doc__.format("file")


def file_mode(m):
    """ Check for a valid file permissions mode. """
    if is_filemode(m):
        return int(m, 8)
    raise ValueError("Not a valid file permissions mode")


def files_list(l, filter_bad=False):
    """ Check if the list contains valid files. """
    l = _str2list(l)
    nl = []
    for f in l:
        if not os.path.isfile(f):
            if not filter_bad:
                raise ValueError("A file from the given list does not exist")
        else:
            nl.append(f)
    if filter_bad and len(nl) == 0:
        raise ValueError("No valid file in the given list")
    return nl
files_list.__name__ = "valid files list"


def __files_type(mime=False):
    """ Check if the list contains valid file types. """
    def _wrapper(ftype):
        def _subwrapper(l):
            for f in files_list(l):
                __file_type(mime)(ftype)(f)
            return l
        return _subwrapper
    _wrapper.__name__ = "MIME types"
    return _wrapper
files_mimetype, files_type = __files_type(True), __files_type()
files_mimetype.__doc__ = files_type.__doc__ = __files_type.__doc__


def files_filtered_list(l):
    """ Check if the list contains valid files and discard invalid ones. """
    return files_list(l, True)
files_filtered_list.__name__ = "filtered files list"


def folder_exists(f):
    """ Check that the given folder exists. """
    if not os.path.exists(f):
        raise ValueError("'{}' does not exist".format(f))
    if not os.path.isdir(f):
        raise ValueError("Target exists and is not a folder")
    return f
folder_exists.__name__ = "existing folder"


def folder_exists_or_create(f):
    """ Check that the given folder exists and create it if not existing. """
    if not os.path.exists(f):
        os.makedirs(f)
    if not os.path.isdir(f):
        raise ValueError("Target exists and is not a folder")
    return f
folder_exists_or_create.__name__ = "folder (exists and is not a folder)"

