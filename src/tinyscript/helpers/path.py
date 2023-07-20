# -*- coding: UTF-8 -*-
"""Path-oriented structures derived from pathlib2.Path.

"""
import errno
import importlib
import sys
from mimetypes import guess_type
from pathlib2 import Path as BasePath
from pyminizip import compress_multiple, uncompress
from shutil import copy, copy2, copytree, rmtree
from six import string_types
from tempfile import gettempdir, NamedTemporaryFile as TempFile

from .constants import *
from .compat import u
from .data.types import is_dict, is_list, is_str
from .password import getpass, getrepass
from ..preimports import ctypes, os, random, re


__all__ = __features__ = ["Path", "ConfigPath", "CredentialsPath", "MirrorPath", "ProjectPath", "PythonPath",
                          "TempPath"]


DOUBLE_EXT = re.compile(r"^(.*?)(\.tar\.(?:br|bz2?|gz|lpaq|lzo?|xz|zst|Z))$")
MARKER     = "#TODO:"


class Path(BasePath):
    """ Extension of the base class Path from pathlib2.
    
    :param expand: expand user's path
    :param create: create the directory if it doesn't exist
    :param touch:  create the file if it doesn't exist (mutually exclusive with 'create')
    """

    _flavour = BasePath()._flavour  # fix to AttributeError
    
    def __new__(cls, *parts, **kwargs):
        expand = kwargs.pop("expand", False)
        create = kwargs.pop("create", False)
        touch  = kwargs.pop("touch", False)
        p = super(Path, cls).__new__(cls, *parts, **kwargs)
        if expand:
            p = super(Path, cls).__new__(cls, str(p.expanduser().absolute()), **kwargs)
        if create and touch:
            raise ValueError("Conflicting options ; 'create' creates a folder hwile 'touch' creates a file")
        elif (create or touch) and not p.exists():
            if create:
                p.mkdir(parents=True)  # exist_ok does not work in Python 2
            elif touch:
                p.touch()
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
    def extension(self):
        """ Get the extension based on the stem and suffix. """
        return self.suffix
    
    @property
    def filename(self):
        """ Get the file name, without the complete path. """
        return self.basename
    
    @property
    def mime_type(self):
        """ Get the MIME type of the current Path object. """
        return guess_type(str(self))[0]
    
    @property
    def permissions(self):
        """ Get the permissions of the current Path object. """
        return os.stat(str(self)).st_mode
    
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
    def stem(self):
        """ Stem also handling some common double extensions. """
        try:
            return DOUBLE_EXT.search(self.basename).group(1)
        except AttributeError:
            return super(Path, self).stem
    
    @property
    def suffix(self):
        """ Suffix also handling some common double extensions. """
        try:
            return DOUBLE_EXT.search(self.basename).group(2)
        except AttributeError:
            return super(Path, self).suffix
    
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
        """ Allows to append bytes to the file, as only write_bytes is available in pathlib2, overwritting the former
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
        """ Allows to append text to the file, as only write_text is available in pathlib2, overwritting the former text
             at each write. """
        return self.__add_text(text, 'a', encoding, errors)
    
    def choice(self, *filetypes):
        """ Return a random file from the current directory. """
        if not self.is_dir():
            return self
        filetypes = list(filetypes)
        while len(filetypes) > 0:
            filetype = random.choice(filetypes)
            filetypes.remove(filetype)
            l = list(self.iterfiles(filetype, filename_only=True))
            if len(l) > 0:
                return self.joinpath(random.choice(l))
    
    def copy(self, new_path, **kwargs):
        """ Copy this folder or file to the given destination. """
        try:
            copytree(str(self), str(new_path), **kwargs)
        except OSError as e:  # does not use NotADirectoryError as it is only available from Python3
            if e.errno == errno.ENOTDIR:
                (copy2 if kwargs.pop('metadata', True) else copy)(str(self), str(new_path), **kwargs)
            else:
                return self
        return self.__class__(new_path)
    
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
                f = lambda p: re.search(r, p.basename) is not None
        else:
            f = lambda p: re.search(name, p.basename) is not None
        for item in self.walk(filter_func=f):
            yield item
    
    def generate(self, prefix="", suffix="", length=8, alphabet="0123456789abcdef"):
        """ Generate a random folder name. """
        # simply return self if it exists and it is not a directory
        if self.exists() and not self.is_dir():
            return self
        # ensure this is a newly generated path
        while True:
            new = self.joinpath(str(prefix) + "".join(random.choice(alphabet) for i in range(length)) + str(suffix))
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
    
    def iterfiles(self, filetype=None, filename_only=False, relative=False):
        """ List all files from the current directory. """
        for i in self.iterdir():
            if i.is_file() and (filetype is None or i.suffix == filetype):
                yield i.filename if filename_only else i.relative_to(self) if relative else i
    
    def iterpubdir(self):
        """ List all visible subdirectories from the current directory. """
        for i in self.iterdir():
            if i.is_dir() and not i.is_hidden():
                yield i
    
    def listdir(self, filter_func=lambda p: True, sort=True):
        """ List the current path using the given filter. """
        try:
            l = os.listdir(str(self))
        except OSError:
            return
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
    
    def remove(self, error=True):
        """ Extension for removing a directory or a file. """
        try:
            rmtree(str(self)) if self.is_dir() else os.remove(str(self))
        except OSError:
            if error:
                raise
    
    def walk(self, breadthfirst=True, filter_func=lambda p: True, sort=True, base_cls=True, relative=False):
        """ Walk the current path for directories and files using os.listdir(), breadth-first or depth-first, sorted or
             not, based on a filter function. """
        rel = lambda i: i.relative_to(self) if relative else i
        out = lambda i: Path(str(i)) if base_cls else i
        if breadthfirst:
            for item in self.listdir(lambda p: not p.is_dir(), sort):
                if filter_func(item):
                    yield out(rel(item))
        for item in self.listdir(lambda p: p.is_dir(), sort):
            if self.is_symlink() and self.resolve() == self.parent:
                continue  # e.g.: /usr/bin/X11 -> /usr/bin
            if breadthfirst and filter_func(item):
                yield out(rel(item))
            for subitem in item.walk(breadthfirst, filter_func, sort, base_cls):
                yield out(rel(subitem))
            if not breadthfirst and filter_func(item):
                yield out(rel(item))
        if not breadthfirst:
            for item in self.listdir(lambda p: not p.is_dir(), sort):
                if filter_func(item):
                    yield out(rel(item))
    
    def write_bytes(self, data):
        """ Fix to non-existing method in Python 2. """
        with self.open(mode='wb') as f:
            return f.write(memoryview(data))
    
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


class CredentialsPath(Path):
    """ Extension of the class Path for handling a path to a file containing credentials.
    
    Note: Beware that this does not handle any security (no obfuscation, hashing or encryption) ; so, any secret entered
           in an instance will remain in memory until this is freed.
    
    :param id:     identifier
    :param secret: secret
    """
    def __new__(cls, *parts, **kwargs):
        p = Path(*parts)
        path, fn = (str(p), "creds.txt") if p.suffix == "" else (p.dirname, p.filename)
        kw = {'create': True, 'expand': True}
        path = Path(*parts, **kw)
        kwargs['exist_ok'] = True
        kwargs['create'] = False
        self = super(CredentialsPath, cls).__new__(cls, str(path), fn, **kwargs)
        self.id = kwargs.get("id") or ""
        self.secret = kwargs.get("secret") or ""
        d = kwargs.get("delimiter") or ":"
        self.save(d) if self.id != "" and self.secret != "" else self.load(d)
        return self
    
    def ask(self, id="Username:", secret="Password:"):
        """ This method allows to ask for credentials.
        
        :param id:     prompt message or (prompt message, validation pattern)
        :param secret: prompt message or (prompt message, validation pattern) or (prompt message, policy dictionary)
        """
        if is_str(id):
            id_prompt, id_pattern = id, None
        elif is_list(id) and len(id) == 2:
            id_prompt, id_pattern = id
        else:
            raise ValueError("Bad identifier ; should be either the prompt message or a 2-tuple with the prompt message"
                             " and the validation pattern")
        id_alias = id_prompt.rstrip(": ").lower().replace(" ", "_")
        if is_str(secret):
            sec_prompt, sec_pattern = secret, None
        elif is_list(secret) and len(secret) == 2:
            sec_prompt, sec_pattern = secret
        else:
            raise ValueError("Bad secret ; should be either the prompt message, a 2-tuple with the prompt message"
                             " and the validation pattern or a 2-tuple with the prompt message and a policy")
        sec_alias = sec_prompt.rstrip(": ").lower().replace(" ", "_")
        self.id = ""
        # too expensive to load the underlying packages ; import only when .ask(...) is called
        from .inputs import user_input
        while self.id == "":
            self.id = user_input(id_prompt, required=True)
            if id_pattern and not re.search(id_pattern, self.id):
                raise ValueError("Bad %s" % id_alias)
        self.secret = ""
        try:
            self.secret = (getpass if is_dict(sec_pattern) else getrepass)(sec_prompt, None, sec_pattern).strip()
        except ValueError as e:
            raise e("Non-compliant %s:\n- %s" % (sec_alias, "\n- ".join(e.errors))) if hasattr(e, "errors") else e
    
    def load(self, delimiter=":"):
        """ This loads credentials from the path taking a delimiter (default: ":") into account. """
        if not self.exists():
            return
        c = self.read_text().strip()
        if c == "":
            return
        try:
            self.id, self.secret = c.split(delimiter)
        except ValueError:
            raise ValueError("Bad delimiter '%s' ; it should not be a character present in the identifier or secret" % \
                             delimiter)
    
    def save(self, delimiter=":"):
        """ This saves the defined credentials to the path taking a delimiter (default: ":") into account. """
        if self.id == "" and self.secret == "":
            return
        self.touch(0o600)
        if delimiter in self.id or delimiter in self.secret:
            raise ValueError("Bad delimiter '%s' ; it should not be a character present in the identifier or secret" % \
                             delimiter)
        self.write_text("%s%s%s" % (self.id, delimiter, self.secret))


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
        """ This method compresses the content of the given source path into the given archive as the destination
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
        """ This method decompresses the given archive, eventually given a password.

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
            try:
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
            except UnicodeDecodeError:
                pass
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
    def __init__(self, path, remove_cache=False):
        super(PythonPath, self).__init__()
        if remove_cache:
            f = (lambda x: x.is_file() and x.extension == ".pyc") if PYTHON2 else \
                (lambda x: x.is_dir() and x.basename == "__pycache__")
            for p in self.walk(filter_func=f):
                p.remove(False)
        if self.is_dir():
            self.modules, _cached = [], []
            for e in [".pyc", ".py"]:
                for p in self.walk(filter_func=lambda x: x.extension == e, base_cls=False):
                    if not p.is_file() or str(p.absolute()) in _cached:
                        continue
                    if e == ".pyc" and (PYTHON3 and p.absolute().dirname.parts[-1] == "__pycache__" or PYTHON2):
                        parts = p.filename.split(".")
                        if PYTHON3 and len(parts) == 3 and re.match(r".?python\-?[23]\d", parts[-2]) or PYTHON2:
                            d = p.absolute().dirname
                            d = d if PYTHON2 else d.parent
                            _cached.append(str(d.joinpath("%s.py" % parts[0])))
                    p = PythonPath(p)
                    if p.loaded:
                        self.modules.append(p.module)
        else:
            self.loaded = False
            if self.extension in [".py", ".pyc"]:
                try:
                    loader_cls = ["SourcelessFileLoader", "SourceFileLoader"][self.extension == ".py"]
                    loader = getattr(importlib.machinery, loader_cls)(self.stem, str(self))
                    spec = importlib.util.spec_from_file_location(self.stem, str(self), loader=loader)
                    self.module = importlib.util.module_from_spec(spec)
                    sys.modules[self.module.__name__] = self.module
                    loader.exec_module(self.module)
                    self.loaded = True
                except (ImportError, NameError, SyntaxError, ValueError):
                    raise
    
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
                return super(TempPath, cls).__new__(cls, p.generate(**kw), **kwargs)
            return super(TempPath, cls).__new__(cls, p, **kwargs)
        else:
            sp = p.joinpath(*parts)
            if sp.is_under(p):
                return super(TempPath, cls).__new__(cls, sp, **kwargs)
            raise ValueError("The given path shall be under '{}'".format(p))
    
    def tempdir(self, dirname=None, **kwargs):
        """ Create and return a TempPath subdirectory instance. """
        return TempPath(self.generate(**kwargs) if dirname is None else self.joinpath(dirname))
    
    def tempfile(self, filename=None, **kwargs):
        """ Instantiate a NamedTemporaryFile or use an existing file in the TempPath and return it as a Path object. """
        return Path(TempFile(dir=str(self), **kwargs).name if filename is None else self.joinpath(filename))

