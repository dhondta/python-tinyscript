# -*- coding: UTF-8 -*-
"""Path-oriented structures derived from pathlib.Path.

"""
import ctypes
import imp
import importlib
import os
import re
from mimetypes import guess_type
from pathlib import Path as BasePath
from pygments.lexers import Python2Lexer
from pyminizip import compress_multiple, uncompress
from random import choice
from re import search
from shutil import rmtree
from six import string_types
from tempfile import gettempdir, NamedTemporaryFile as TempFile

from .constants import *
from .compat import u
from .password import getpass


__all__ = __features__ = ["Path", "ConfigPath", "MirrorPath", "ProjectPath", "PythonPath", "TempPath"]


MARKER = "#TODO:"

# NB: PythonLexer.analyse_text only relies on shebang !
_lexer = Python2Lexer()


class Path(BasePath):
    """ Extension of the base class Path from pathlib.
    
    :param expand: expand user's path
    :param create: create the directory if it doesn't exist
    """
    _flavour = BasePath()._flavour  # fix to AttributeError
    
    def __new__(cls, *parts, **kwargs):
        expand = kwargs.pop("expand", False)
        create = kwargs.pop("create", False)
        p = super(Path, cls).__new__(cls, *parts, **kwargs)
        if expand:
            p = p.expanduser().absolute()
        if create and not p.exists():
            p.mkdir(parents=True)  # exist_ok does not work in Python 2
        return p
    
    @property
    def basename(self):
        """ Dummy alias for name attribute. """
        return self.name
    
    @property
    def bytes(self):
        """ Get file's content as bytes. """
        with self.open('rb') as f:
            return f.read()
    
    @property
    def child(self):
        """ Get the child path relative to self's one. """
        return Path(*self.parts[1:])
    
    @property
    def dirname(self):
        """ Get the directory name. """
        return self if self.is_dir() else self.parent
    
    @property
    def filename(self):
        """ Get the file name, without the complete path. """
        return self.stem + self.suffix
    
    @property
    def mime_type(self):
        """ Get the MIME type of the current Path object. """
        return guess_type(str(self))[0]
    
    @property
    def size(self):
        """ Get path's size. """
        if self.is_file() or self.is_symlink():
            return self.stat().st_size
        elif self.is_dir():
            s = 4096  # include the size of the directory itself
            for root, dirs, files in os.walk(str(self)):
                s += 4096 * len(dirs)
                for f in files:
                    s += os.stat(str(Path(root).joinpath(f))).st_size
            return s
    
    @property
    def text(self):
        """ Get file's content as a string. """
        return self.read_text()
    
    def __add_text(self, data, mode='w', encoding=None, errors=None):
        """ Allows to write/append text to the file, both in Python 2 and 3. """
        if not isinstance(data, string_types):
            raise TypeError("data must be str, not %s" % 
                            data.__class__.__name__)
        with self.open(mode=mode, encoding=encoding, errors=errors) as f:
            return f.write(u(data))
    
    def append_bytes(self, data):
        """ Allows to append bytes to the file, as only write_bytes is available in pathlib, overwritting the former
             bytes at each write. """
        with self.open(mode='ab') as f:
            return f.write(memoryview(data))
    
    def append_line(self, line):
        """ Shortcut for appending a single line (text with newline). """
        self.append_text(["\n", ""][self.size == 0] + line)
    
    def append_lines(self, *lines):
        """ Shortcut for appending a bunch of lines. """
        for line in lines:
            self.append_line(line)
    
    def append_text(self, text, encoding=None, errors=None):
        """ Allows to append text to the file, as only write_text is available in pathlib, overwritting the former text
             at each write. """
        return self.__add_text(text, 'a', encoding, errors)
    
    def choice(self, *filetypes):
        """ Return a random file from the current directory. """
        if not self.is_dir():
            return self
        filetypes = list(filetypes)
        while len(filetypes) > 0:
            filetype = choice(filetypes)
            filetypes.remove(filetype)
            l = list(self.iterfiles(filetype, filename_only=True))
            if len(l) > 0:
                return self.joinpath(choice(l))
    
    def expanduser(self):
        """ Fixed expanduser() method, working for both Python 2 and 3. """
        return Path(os.path.expanduser(str(self)))
    
    def find(self, name=None, regex=False):
        """ Find a folder or file from the current path. """
        if name is None:
            f = lambda p: True
        elif not regex:
            if "*" not in name:
                f = lambda p: p.basename == name
            else:
                r = "^{}$".format(name.replace(".", "\\.").replace("?", "\\?").replace("-", "\\-").replace("+", "\\+")
                                      .replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)")
                                      .replace("{", "\\{").replace("}", "\\}").replace("*", ".*"))
                f = lambda p: search(r, p.basename) is not None
        else:
            f = lambda p: search(name, p.basename) is not None
        for item in self.walk(filter_func=f):
            yield item
    
    def generate(self, prefix="", suffix="", length=8, alphabet="0123456789abcdef"):
        """ Generate a random folder name. """
        if not self.is_dir():
            return self
        while True:
            _ = "".join(choice(alphabet) for i in range(length))
            new = self.joinpath(str(prefix) + _ + str(suffix))
            if not new.exists():
                return new
    rand_folder_name = generate
    
    def is_hidden(self):
        """ Check if the current path is hidden. """
        if DARWIN:
            fnd = importlib.import_module("Foundation")
            u, f = fnd.NSURL.fileURLWithPath_(str(self)), fnd.NSURLIsHiddenKey
            return u.getResourceValue_forKey_error_(None, f, None)[1]
        elif LINUX:
            return self.stem.startswith(".")
        elif WINDOWS:
            import win32api, win32con
            return win32api.GetFileAttributes(p) & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
        raise NotImplementedError("Cannot check for the hidden status on this platform")
    
    def is_samepath(self, otherpath):
        """ Check if both paths have the same parts. """
        return self.absolute().parts == Path(otherpath).absolute().parts
    
    def is_under(self, parentpath):
        """ Check if the path is under a parent path. """
        p = Path(parentpath)
        if not p.is_dir():
            p = Path(p.dirname)
        return p in self.parents
    
    def iterfiles(self, filetype=None, filename_only=False):
        """ List all files from the current directory. """
        for i in self.iterdir():
            if i.is_file() and (filetype is None or i.suffix == filetype):
                yield i.filename if filename_only else i
    
    def iterpubdir(self):
        """ List all visible subdirectories from the current directory. """
        for i in self.iterdir():
            if i.is_dir() and not i.is_hidden():
                yield i
    
    def listdir(self, filter_func=lambda p: True, sort=True):
        """ List the current path using the given filter. """
        l = os.listdir(str(self))
        if sort:
            l = sorted(l)
        for item in l:
            item = self.joinpath(item)
            if filter_func(item):
                yield item
    
    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """ Fix to non-existing argument exist_ok in Python 2. """
        arg = (exist_ok, ) if PYTHON3 else ()
        super(Path, self).mkdir(mode, parents, *arg)
    
    def read_lines(self, encoding=None, errors=None):
        """ Extra method for reading a file as lines. """
        for l in self.read_text(encoding, errors).splitlines():
            yield l
    
    def read_text(self, encoding=None, errors=None):
        """ Fix to non-existing method in Python 2. """
        with self.open(mode='r', encoding=encoding, errors=errors) as f:
            return f.read()
    
    def reset(self):
        """ Ensure the file exists and is empty. """
        with self.open('w') as f:
            pass
    
    def remove(self):
        """ Extension for removing a directory or a file. """
        if self.is_dir():
            rmtree(str(self))
        else:
            os.remove(str(self))
    
    def walk(self, breadthfirst=True, filter_func=lambda p: True, sort=True, base_cls=True):
        """ Walk the current path for directories and files using os.listdir(), breadth-first or depth-first, sorted or
             not, based on a filter function. """
        if breadthfirst:
            for item in self.listdir(lambda p: not p.is_dir(), sort):
                if filter_func(item):
                    yield Path(str(item)) if base_cls else item
        for item in self.listdir(lambda p: p.is_dir(), sort):
            if breadthfirst and filter_func(item):
                yield Path(str(item)) if base_cls else item
            for subitem in item.walk(breadthfirst, filter_func):
                yield Path(str(subitem)) if base_cls else subitem
            if not breadthfirst and filter_func(item):
                yield Path(str(item)) if base_cls else item
        if not breadthfirst:
            for item in self.listdir(lambda p: not p.is_dir(), sort):
                if filter_func(item):
                    yield Path(str(item)) if base_cls else item
    
    def write_text(self, data, encoding=None, errors=None):
        """ Fix to non-existing method in Python 2. """
        return self.__add_text(data, 'w', encoding, errors)


class ConfigPath(Path):
    """ Extension of the class Path for handling a temporary path.
    
    :param app:  application name for naming the config file or folder
    :param file: whether the target should be a config file or folder
    """
    def __new__(cls, app, **kwargs):
        isfile = kwargs.pop('file', False)
        kwargs['create'] = not isfile
        kwargs["expand"] = True
        path = os.path.join(os.environ['LOCALAPPDATA'], [app, app + ".conf"][isfile]) if WINDOWS else \
               os.path.join("Library", "Application Support", [app, app + ".conf"][isfile]) if DARWIN else \
               [os.path.join(".config", app.lower()), "." + app.lower() + ".conf"][isfile]
        self = super(ConfigPath, cls).__new__(cls, os.path.join("~", path), **kwargs)
        self._isfile = isfile
        return self


class MirrorPath(Path):
    """ Extension of the class Path for handling a folder that can mirror another one using symbolic links.
    
    :param destination: destination folder where the structure is mirrored
    :param source:      source folder from which the structure is mirrored
    """
    def __new__(cls, destination, source=None, **kwargs):
        self = super(MirrorPath, cls).__new__(cls, destination, **kwargs)
        if source is not None:
            self.mirror(source)
        return self
    
    def mirror(self, source):
        """ Mirror the source item. """
        self._mirrored = []
        source = Path(source)
        if not self.exists():
            self.symlink_to(str(source.absolute()), source.is_dir())
        elif not self.is_symlink() and source.is_dir():
            for item in os.listdir(str(source)):
                dst, src = self.joinpath(item), source.joinpath(item)
                self._mirrored.append(MirrorPath(dst, src))
    
    def unmirror(self):
        """ Perform the reverse operation of mirror. """
        while len(self._mirrored) > 0:
            self._mirrored.pop(0).unmirror()
        if self.is_symlink():
            self.unlink()


class ProjectPath(Path):
    def __new__(cls, root=".", structure=None, **kwargs):
        self = super(ProjectPath, cls).__new__(cls, root, **kwargs)
        if self.mime_type == "application/zip":
            self.is_archive = True
        elif self.is_file():
            raise ValueError("Bad project archive file ; should be ZIP")
        else:
            self.is_archive = False
            structure = structure or {}
            self.create(structure, root)
        return self
    
    def archive(self, path=None, password=None, ask=False, remove=True, **kwargs):
        """ This function compresses the content of the given source path into the given archive as the destination
             path, eventually given a password.

        :param path:     path to the project folder to be archived
        :param password: password string to be passed
        :param ask:      whether a password should be asked or not
        :param remove:   remove after compression
        """
        if self.is_archive:
            raise ValueError("Already an archive")
        password = getpass() if ask else password
        dst = Path(path or (str(self) + ".zip"))
        src_list, dst_list = [], []
        for f in self.walk(filter_func=lambda p: p.is_file()):
            src_list.append(str(f))
            dst_list.append(str(f.relative_to(self).dirname))
        # Pyminizip changes the current working directory after creation of an archive ; so backup the current
        #  working directory to restore it after compression
        cwd = os.getcwd()
        compress_multiple(src_list, dst_list, str(dst), password or "", 9)
        os.chdir(cwd)
        if remove:
            self.remove()
        return ProjectPath(dst)
    
    def create(cls, structure, root="."):
        p = Path(root, create=True)
        for k, v in structure.items():
            sp = p.joinpath(k)
            if isinstance(v, dict):
                cls.create(v, sp)
            elif v is None:
                sp.touch()
            else:
                sp.write_text(str(v))
    
    def load(self, path=None, password=None, ask=False, remove=True, **kwargs):
        """ This function decompresses the given archive, eventually given a password.

        :param path:     path to the archive to be extracted
        :param password: password string to be passed
        :param ask:      whether a password should be asked or not
        :param remove:   remove after decompression
        """
        if not self.is_archive:
            raise ValueError("Not an archive")
        password = getpass() if ask else password
        dst = Path(path or str(self.dirname.joinpath(self.stem)), create=True)
        # Pyminizip changes the current working directory after extraction of an archive ; so backup the current
        #  working directory to restore it after decompression
        cwd = os.getcwd()
        uncompress(str(self), password or "", str(dst), False)
        os.chdir(cwd)
        if remove:
            self.remove()
        return ProjectPath(dst)
    
    def search(self, pattern):
        """ Walk the project folder for a given pattern. """
        matches = {}
        for p in self.walk(filter_func=lambda p: p.is_file()):
            current_cls, line_number = None, None
            with p.open() as f:
                for i, l in enumerate(f):
                    if "class " in l:
                        current_cls = l.split("class ")[1].split("(")[0].strip()
                    if "def " in l:
                        line_number = str(i + 1)
                    match = re.search(pattern, l)
                    if match:
                        m = str(Path(p))
                        if current_cls is not None:
                            m += ":" + current_cls
                        m += ":" + (line_number or str(i + 1))
                        try:
                            matches[m] = match.group(1)
                        except IndexError:
                            matches[m] = l
        return matches
    
    @property
    def fixme(self):
        """ Walk the folder for FIXME statements. """
        return self.search(r"#\s?FIXME:\s+(.*)$")
    
    @property
    def todo(self):
        """ Walk the folder for TODO statements. """
        return self.search(r"#\s?TODO:\s+(.*)$")


class PythonPath(Path):
    """ Path extension for handling the dynamic import of Python modules. """
    def __init__(self, path):
        super(PythonPath, self).__init__()
        try:
            self.is_pymodule = self.is_file() and _lexer.analyse_text(self.open().read()) == 1.0
        except UnicodeDecodeError:
            self.is_pymodule = False
        if self.is_dir():
            self.modules = []
            for p in self.walk(base_cls=False):
                p = PythonPath(p)
                if p.is_pymodule:
                    self.modules.append(p.module)
        else:
            if self.is_pymodule:
                self.module = imp.load_source(self.stem, str(self))
    
    @property
    def classes(self):
        if hasattr(self, "module"):
            modules = [self.module]
        elif hasattr(self, "modules"):
            modules = self.modules
        else:
            return
        l = []
        for m in modules:
            for n in dir(m):
                c = getattr(m, n)
                try:
                    issubclass(c, c)
                    l.append(c)
                except TypeError:
                    pass
        return l
    
    def get_classes(self, *base_cls):
        """ Yield a list of all subclasses inheriting from the given class from the Python module. """
        if len(base_cls) == 0:
            base_cls = (object, )
        for c in self.classes or []:
            if issubclass(c, base_cls) and c not in base_cls:
                yield c
    
    def has_baseclass(self, base_cls):
        """ Check if the Python module has the given base class. """
        return self.has_class(base_cls, False)
    
    def has_class(self, cls, self_cls=True):
        """ Check if the Python module has the given class. """
        for c in self.classes or []:
            if issubclass(c, cls) and (self_cls or c is not cls):
                return True
        return False


class TempPath(Path):
    """ Extension of the class Path for handling a temporary path.
    
    :param prefix:   prefix for the temporary folder name
    :param suffix:   suffix for the temporary folder name
    :param length:   length for the folder name (if 0, do not generate a folder name, e.g. keeping /tmp)
    :param alphabet: character set to be used for generating the folder name
    """
    def __new__(cls, *parts, **kwargs):
        kwargs["create"] = True   # force creation
        kwargs["expand"] = False  # expansion is not necessary
        p = Path(gettempdir())
        if len(parts) == 0:
            kw = {}
            kw["prefix"]   = kwargs.pop("prefix", "")
            kw["suffix"]   = kwargs.pop("suffix", "")
            kw["length"]   = kwargs.pop("length", 0)
            kw["alphabet"] = kwargs.pop("alphabet", "0123456789abcdef")
            if kw["length"] > 0:
                while True:
                    # ensure this is a newly generated path
                    tmp = p.generate(**kw)
                    if not tmp.exists():
                        break
                return super(TempPath, cls).__new__(cls, tmp, **kwargs)
            return super(TempPath, cls).__new__(cls, p, **kwargs)
        else:
            sp = Path(*parts)
            if sp.is_under(p):
                return super(TempPath, cls).__new__(cls, sp if sp.is_dir() else sp.dirname, **kwargs)
            raise ValueError("The given path shall be under '{}'".format(p))
    
    def tempfile(self, filename=None, **kwargs):
        """ Instantiate a NamedTemporaryFile or use an existing file in the TempPath and return it as a Path object. """
        return Path(TempFile(dir=str(self), **kwargs).name) if filename is None else self.joinpath(filename)

