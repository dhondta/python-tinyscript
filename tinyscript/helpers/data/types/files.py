# -*- coding: UTF-8 -*-
"""Files/Folders-related checking functions and argument types.

"""
from os import access, makedirs, X_OK
from os.path import exists, isdir, isfile

from .strings import _str2list


__all__ = __features__ = []


# dummy shortcuts, compliant with the is_* naming convention
__all__ += ["is_dir", "is_executable", "is_file", "is_folder"]
is_dir = is_folder = isdir
is_executable = lambda f: access(f, X_OK)
is_file = isfile


# file and folder-related argument types
__all__ += ["file_does_not_exist", "file_exists", "files_list",
            "files_filtered_list", "folder_does_not_exist", "folder_exists",
            "folder_exists_or_create"]


def file_does_not_exist(f):
    """ Check that the given file does not exist. """
    if exists(f):
        raise ValueError("'{}' already exists".format(f))
    return f
folder_does_not_exist = file_does_not_exist


def file_exists(f):
    """ Check that the given file exists. """
    if not exists(f):
        raise ValueError("'{}' does not exist".format(f))
    if not isfile(f):
        raise ValueError("Target exists and is not a file")
    return f


def files_list(l, filter_bad=False):
    """ Check if the list contains valid files. """
    l = _str2list(l)
    nl = []
    for f in l:
        if not isfile(f):
            if not filter_bad:
                raise ValueError("A file from the given list does not exist")
        else:
            nl.append(f)
    if filter_bad and len(nl) == 0:
        raise ValueError("No valid file in the given list")
    return nl


def files_filtered_list(l):
    """ Check if the list contains valid files and discard invalid ones. """
    return files_list(l, True)


def folder_exists(f):
    """ Check that the given folder exists. """
    if not exists(f):
        raise ValueError("'{}' does not exist".format(f))
    if not isdir(f):
        raise ValueError("Target exists and is not a folder")
    return f


def folder_exists_or_create(f):
    """ Check that the given folder exists and create it if not existing. """
    if not exists(f):
        makedirs(f)
    if not isdir(f):
        raise ValueError("Target exists and is not a folder")
    return f
