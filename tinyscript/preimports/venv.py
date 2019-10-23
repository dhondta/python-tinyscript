# -*- coding: UTF-8 -*-
"""Module for enhancing virtualenv preimport.

"""
import os
import site
import sys
import virtualenv
from shutil import rmtree
from six import string_types
from time import sleep
try:  # will work in Python 3
    from pip._internal.main import main as _pip_main
except ImportError:
    from pip._internal import main as _pip_main

from ..helpers import JYTHON, PYPY, WINDOWS


__ORIGINAL_PATH    = os.environ['PATH']
__ORIGINAL_SPATH   = sys.path[:]
__ORIGINAL_SPREFIX = sys.prefix


def __activate(venv_dir):
    """
    This activates a virtual environment.
    
    :param venv_dir: virtual environment's directory
    """
    j = os.path.join
    bin_dir = j(venv_dir, "bin")
    path = os.environ.get("PATH", "").split(os.pathsep)
    os.environ["PATH"] = os.pathsep.join([bin_dir] + path)
    os.environ["VIRTUAL_ENV"] = venv_dir
    site_packages = j(venv_dir, "Lib", "site-packages") if JYTHON else \
                    j(venv_dir, "site-packages") if PYPY else \
                    j(venv_dir, "Lib", "site-packages") if WINDOWS else \
                    j(venv_dir, "lib", "python{}.{}".format(*sys.version_info),
                      "site-packages")
    old = set(sys.path)
    site.addsitedir(site_packages)
    new = list(sys.path)
    sys.path = [i for i in new if i not in old] + [i for i in new if i in old]
    sys.real_prefix = sys.prefix
    sys.prefix = venv_dir


def __deactivate():
    """
    This deactivates a virtual environment.
    
    :param venv_dir: virtual environment's directory
    """
    # reset all values modified by activate_this.py
    os.environ['PATH']            = __ORIGINAL_PATH
    os.environ['VIRTUAL_ENV']     = ""
    os.environ['PIP_REQ_TRACKER'] = ""
    sys.path                      = __ORIGINAL_SPATH[:]
    sys.prefix                    = __ORIGINAL_SPREFIX
    try:
        delattr(sys, "real_prefix")
    except AttributeError:
        pass


def __install(package, *args, **kwargs):
    """
    Python2/3-compatible Pip install function.
    
    :param package: package name
    :param args:    options to be used with the pip install command
    :param kwargs:  keyword-arguments to be used with the pip install command
    """
    cmd = ["install", "-U"]
    for v in args:
        cmd.append(str(v))
    for k, v in kwargs.items():
        cmd.append("--" + k.replace("_", "-"))
        cmd.append(str(v))
    cmd.append(package.strip())
    _pip_main(cmd)


def __setup(venv_dir, requirements=None):
    """
    This creates (if relevant) and activates a virtual environment. It also
     allows to define requirements to be installed in this environment.
    
    :param venv_dir:     virtual environment's directory
    :param requirements: list of required package OR path of the requirements
                          file to be used
    """
    __deactivate()
    venv_dir = os.path.abspath(venv_dir)
    if not os.path.exists(venv_dir):
        virtualenv.create_environment(venv_dir)
    __activate(venv_dir)
    if isinstance(requirements, string_types):
        with open(requirements) as f:
            requirements = [l.strip() for l in f]
    if isinstance(requirements, (tuple, list, set)):
        for req in requirements:
            __install(req, prefix=venv_dir)


def __teardown(venv_dir=None):
    """
    This deactivates and removes the given virtual environment or the one
     defined in the related environment variable.

    :param venv_dir: virtual environment's directory
    """
    venv = venv_dir or os.environ.get('VIRTUAL_ENV', "")
    if venv:
        __deactivate()
        rmtree(venv, True)
        while os.path.isdir(venv): sleep(1)


class VirtualEnv(object):
    """
    This context manager simplifies the use of a virtual environment.
    
    :param venv_dir:     virtual environment's directory
    :param requirements: list of required package OR path of the requirements
                          file to be used
    :param remove:       whether the virtual environment is to be removed after
                          the entered context
    """
    def __init__(self, venv_dir, requirements=None, remove=False):
        self.__remove = remove
        self.__requirements = requirements
        self.__venv_dir = venv_dir

    def __enter__(self):
        self.setup(self.__venv_dir, self.__requirements)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        getattr(self, ["deactivate", "teardown"][self.__remove])()
    
    def __getattr__(self, name):
        return getattr(virtualenv, name) if hasattr(virtualenv, name) else \
               super().__getattr__(name)


virtualenv.activate   = __activate
virtualenv.deactivate = __deactivate
virtualenv.install    = __install
virtualenv.setup      = __setup
virtualenv.teardown   = __teardown
virtualenv.VirtualEnv = VirtualEnv
