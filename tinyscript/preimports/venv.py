# -*- coding: UTF-8 -*-
"""Module for enhancing virtualenv preimport.

"""
import os
import re
import site
import sys
import virtualenv
from importlib import import_module
from pip._internal.cli.main_parser import parse_command
from pip._internal.exceptions import PipError
from shutil import rmtree
from six import string_types
from slugify import slugify
from subprocess import Popen, PIPE

from ..helpers import Path, JYTHON, PYPY, WINDOWS


__ORIGINAL_PATH        = os.environ['PATH']
__ORIGINAL_SYSPATH     = sys.path[:]
__ORIGINAL_SYSPREFIX   = sys.prefix
__ORIGINAL_SYSRPREFIX  = getattr(sys, "real_prefix", None)
# package regex for parsing a line with [package]-[version] format
PREGEX = re.compile(r"\s?([a-zA-Z\-_]+?)\-((?:\d+)(?:\.?[a-z]*\d+)+)")


def __activate(venv_dir):
    """
    This activates a virtual environment.
    
    :param venv_dir: virtual environment's directory
    """
    venv_dir = os.path.abspath(venv_dir)
    if not os.path.isdir(venv_dir):
        raise NotAVirtualEnv("Bad virtual environment")
    j = os.path.join
    bin_dir = j(venv_dir, "bin")
    _ = __ORIGINAL_PATH.split(os.pathsep)
    os.environ["PATH"] = os.pathsep.join([bin_dir] + _)
    os.environ["VIRTUAL_ENV"] = venv_dir
    site_packages = j(venv_dir, "Lib", "site-packages") if JYTHON else \
                    j(venv_dir, "site-packages") if PYPY else \
                    j(venv_dir, "Lib", "site-packages") if WINDOWS else \
                    j(venv_dir, "lib", "python{}.{}".format(*sys.version_info), "site-packages")
    old = set(__ORIGINAL_SYSPATH)
    site.addsitedir(site_packages)
    new = list(sys.path)
    sys.path = [i for i in new if i not in old] + [i for i in new if i in old]
    sys.real_prefix = __ORIGINAL_SYSRPREFIX or __ORIGINAL_SYSPREFIX
    sys.prefix = venv_dir
virtualenv.activate = __activate


def __check_pip_req_tracker():
    """
    This checks if the temporary folder of the Pip requirements tracker still exists and corrects the related
     environment variable accordingly.
    """
    pip_reqt = os.environ.get('PIP_REQ_TRACKER')
    if pip_reqt is not None and not os.path.exists(pip_reqt):
        os.environ['PIP_REQ_TRACKER'] = ""


def __deactivate():
    """
    This deactivates a virtual environment.
    
    :param venv_dir: virtual environment's directory
    """
    # reset all values modified by activate_this.py
    os.environ['PATH']        = __ORIGINAL_PATH
    os.environ['VIRTUAL_ENV'] = ""
    sys.path                  = __ORIGINAL_SYSPATH[:]
    sys.prefix                = __ORIGINAL_SYSPREFIX
    try:
        # from a normal environment, this key should not exist
        delattr(sys, "real_prefix")
        # but it is important to also reset it if the script was itself run from a virtual environment
        if __ORIGINAL_SYSRPREFIX is not None:
            sys.real_prefix = __ORIGINAL_SYSRPREFIX
    except:
        pass
    __check_pip_req_tracker()
virtualenv.deactivate = __deactivate


def __get_virtualenv(error=True):
    """
    This gets the currently defined virtual environment or raises an error if no environment is defined.
    """
    venv = os.environ.get('VIRTUAL_ENV', "")
    if venv == "" and error:
        raise NotAVirtualEnv("Not in a virtual environment")
    return venv


def __install(package, *args, **kwargs):
    """
    Python2/3-compatible Pip install function.
    
    :param package: package name
    :param args:    options to be used with the pip install command
    :param kwargs:  keyword-arguments to be used with the pip install command
    """
    global pip_proc
    __check_pip_req_tracker()
    verbose = "-v" in args or "--verbose" in args
    if not verbose:
        args += ("-v", )
    error = kwargs.pop("error", False)
    package = package.strip()
    cmd = ["install", "-U"] + __parse_args(*args, **kwargs) + [package]
    for l in __pip_run(cmd):
        if verbose:
            print(l)
        if not error:
            continue
        if l.startswith("pip._internal.exceptions") or l.startswith("DistributionNotFound"):
            pip_proc.kill()
            raise PipError(l.split(": ", 1)[1])
        elif l.startswith("Successfully installed"):
            m = list(filter(lambda p: p[0] == package, PREGEX.findall(l[23:])))
            if len(m) == 0:
                raise PipError("Installation of {} failed".format(package))
    return PipPackage(package, error)
virtualenv.install = __install


def __is_installed(package, *args, **kwargs):
    """
    This checks if a given package is installed in the virtual environment.
    
    :param package: package name
    :param args:    options to be used with the pip list command
    :param kwargs:  keyword-arguments to be used with the pip list command
    """
    found = False
    for name, version in __list_packages(*args, **kwargs):
        if isinstance(package, string_types) and package == name or isinstance(package, (list, tuple, set)) and \
           package[0] == name and package[1] == version:
            found = True
            break
    return found
virtualenv.is_installed = __is_installed


def __list_packages(*args, **kwargs):
    """
    This lists the packages installed in the currently activated or the given virtual environment.
    
    :param venv_dir: virtual environment's directory
    :param args:     options to be used with the pip list command
    :param kwargs:   keyword-arguments to be used with the pip list command
    """
    cmd = ["list"] + __parse_args(*args, **kwargs)
    for line in __pip_run(cmd, False):
        if not ("Package" in line and "Version" in line or "-------" in line or line.strip() == ""):
            yield tuple(_.strip() for _ in line.split(" ", 1))
virtualenv.list_packages = __list_packages


def __parse_args(*args, **kwargs):
    """
    This parses input args and kwargs in a format that suits pip._internal.main.
    """
    l = []
    for v in args:
        if v not in l:
            l.append(str(v))
    for k, v in kwargs.items():
        k = "--" + k.replace("_", "-")
        if k not in l:
            l.append(k)
            if v is not True:
                l.append(str(v))
    return l


def __pip_run(cmd, error=True):
    """
    This runs a Pip command using the binary from the current virtual environment.
    
    :param cmd: the Pip command and its parameters as a list
    """
    global pip_proc
    venv = __get_virtualenv(error)
    parse_command(cmd)
    cmd = ["pip" if venv == "" else os.path.join(venv, "bin", "pip")] + cmd
    pip_proc = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    for line in iter(pip_proc.stdout.readline, ""):
        yield line[:-1]


def __setup(venv_dir, requirements=None, force_reinstall=False, no_cache=True, verbose=False):
    """
    This creates (if relevant) and activates a virtual environment. It also allows to define requirements to be
     installed in this environment.
    
    :param venv_dir:        virtual environment's directory
    :param requirements:    list of required package OR path of the requirements file to be used
    :param force_reinstall: force the reinstallation of required packages
    :param no_cache:        disable the cache
    :param verbose:         displayed Pip output while installing packages
    """
    __deactivate()
    venv_dir = os.path.abspath(venv_dir)
    if not os.path.exists(venv_dir):
        # fix to issue: https://github.com/pypa/virtualenv/issues/1585
        try:
            virtualenv.create_environment(venv_dir)
        except AttributeError:
            virtualenv.cli_run([venv_dir])
        # other issue: https://github.com/pypa/pipenv/issues/4518
        #  for Python3, ImportError when using virtualenv installed with pip ;
        #  works while installed with apt (python3-virtualenv)
    __activate(venv_dir)
    if isinstance(requirements, string_types):
        with open(requirements) as f:
            requirements = [l.strip() for l in f]
    if isinstance(requirements, (tuple, list, set)):
        args = []
        if force_reinstall:
            args.append("--force-reinstall")
        if no_cache:
            args.append("--no-cache-dir")
        if verbose:
            args.append("-v")
        kwargs = {'prefix': venv_dir}
        for req in requirements:
            pkg = __install(req, *args, **kwargs)
            for tl in pkg.top_level:
                if hasattr(virtualenv, tl):
                    raise TopLevelAlreadyExists("{} ({})".format(tl, pkg.name))
                m = import_module(tl)
                setattr(virtualenv, tl, m)
virtualenv.setup = __setup


def __teardown(venv_dir=None):
    """
    This deactivates and removes the given virtual environment or the one defined in the related environment variable.

    :param venv_dir: virtual environment's directory
    """
    venv = venv_dir or os.environ.get('VIRTUAL_ENV', "")
    if venv != "":
        __deactivate()
        rmtree(venv, True)
virtualenv.teardown = __teardown


class PipPackage(object):
    """
    This class is used to represent a Pip package and its attribute.
    """
    def __init__(self, name, error=True):
        self.name = name
        self.top_level = []
        cmd = ["show", name]
        venv = os.environ.get('VIRTUAL_ENV', "")
        for i in range(2):
            for line in globals()['__pip_run'](cmd, False):
                try:
                    k, v = line.strip().split(": ")
                    k = slugify(k).replace("-", "_")
                    if k.startswith("require"):
                        v = v.split(", ")
                    setattr(self, k, v)
                except ValueError:
                    continue
            if hasattr(self, "version") or venv == "":
                break
            else: # after the first guess, if the package was not found, deactivate it to retry with main Pip
                globals()['__deactivate']()
        # afterwards, re-enable the virtual environment if relevant
        if venv != "":
            globals()['__activate'](venv)
        if not hasattr(self, "version"):
            if error:
                raise PipError("Pip package not found: {}".format(name))
        else:
            name = "{}-{}*".format(self.name, self.version)
            try:
                pkgloc = list(Path(self.location).find(name))[0]
                tl = list(pkgloc.find("top_level.txt"))[0]
                self.top_level = tl.read_lines()
            except IndexError:
                pass
virtualenv.PipPackage = PipPackage


class VirtualEnv(object):
    """
    This context manager simplifies the use of a virtual environment.
    
    :param venvdir:      virtual environment's directory
    :param requirements: list of required package OR path of the requirements file to be used
    :param reinstall:    force the reinstallation of required packages
    :param no_cache:     disable the cache
    :param remove:       whether the virtual environment is to be removed after the entered context
    :param verbose:      displayed Pip output while installing packages
    """
    def __init__(self, venvdir=None, requirements=None, remove=False, reinstall=False, no_cache=False, verbose=False):
        self.__no_cache = no_cache
        self.__reinstall = reinstall
        self.__remove = remove
        self.__requirements = requirements
        self.__venv_dir = venvdir or __get_virtualenv()
        self.__verbose = verbose

    def __enter__(self):
        self.setup(self.__venv_dir, self.__requirements, self.__reinstall, self.__no_cache, self.__verbose)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        getattr(self, ["deactivate", "teardown"][self.__remove])()
    
    def __getattr__(self, name):
        try:
            return getattr(virtualenv, name)
        except AttributeError:
            raise AttributeError("object 'VirtualEnv' has no attribute '{}'".format(name))
virtualenv.VirtualEnv = VirtualEnv


class NotAVirtualEnv(Exception):
    pass


class TopLevelAlreadyExists(Exception):
    pass

