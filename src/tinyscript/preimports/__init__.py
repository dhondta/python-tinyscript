# -*- coding: UTF-8 -*-
"""Module for defining the list of preimports.

"""
import lazy_object_proxy
from importlib import import_module, reload


__all__ = __features__ = ["import_module"]
__all__ += ["__imports__", "load", "reload"]

__imports__ = {
    'bad': [],
    'enhanced': {
        'code':       "codep",
        'functools':  "ftools",
        'getpass':    "pswd",
        'hashlib':    "hash",
        'inspect':    "inspectp",
        'itertools':  "itools",
        'logging':    "log",
        'random':     "rand",
        're':         "regex",
        'shutil':     "shutilp",
        'string':     "stringp",
        'virtualenv': "venv",
    },
    'standard': [
        "argparse",
        "ast",
        "base64",
        "binascii",
        "codext",
        "collections",
        "colorful",
        "configparser",
        "ctypes",
        "fileinput",
        "json",
        "os",
        "platform",
        "shlex",
        "signal",
        "string",
        "struct",
        "subprocess",
        "sys",
        "time",
        "types",
        "uuid",
    ],
    'optional': [
        "bs4",
        "fs",
        "loremipsum",
        "requests",
    ]
}


def _load_preimports(*extras, lazy=True):
    """
    This loads the list of modules to be preimported in the global scope.
    
    :param extra: additional modules
    :return:      list of successfully imported modules, list of failures
    """
    i = __imports__
    for module, enhanced in i['enhanced'].copy().items():
        # these modules are used somewhere in the imported code anyway, hence laziness makes no sense
        load(module, enhanced, lazy=module in ["inspect", "logging", "shutil"] or lazy)
        # handle specific classes to be added to the global namespace
        if module == "virtualenv":
            cls = ["PipPackage", "VirtualEnv"]
            for c in cls:
                globals()[c] = lazy_object_proxy.Proxy(lambda: getattr(m, c))
            __features__.extend(cls)
    for module in i['standard'] + list(extras):
        load(module, lazy=lazy)
    for module in i['optional']:
        load(module, optional=True, lazy=lazy)


def load(module, tsmodule=None, optional=False, lazy=True):
    """
    This loads a module and, in case of failure, appends it to a list of bad
     imports or not if it is required or optional.
    
    :param module:   module name
    :param tsmodule: Tinyscript root submodulen (in case of internal import)
    :param optional: whether the module is optional or not
    :param lazy:     lazily load the module using a Proxy object
    """
    global __features__, __imports__
    m, tsmodule = globals().get(module), (module, ) if tsmodule is None else ("." + tsmodule, "tinyscript.preimports")
    if m is not None:  # already imported
        __features__.append(module)
        return m
    def _load():
        try:
            m = import_module(*tsmodule)
            if len(tsmodule) == 2:
                m = getattr(m, module)
            globals()[module] = m
            m.__name__ = module
            return m
        except ImportError:
            if module in __features__:
                __features__.remove(module)
            if not optional and module not in __imports__['bad']:
                __imports__['bad'].append(module)
                for k, x in __imports__.items():
                    if k != 'bad' and module in x:
                        x.remove(module) if isinstance(x, list) else x.pop(module)
    __features__.append(module)
    globals()[module] = m = lazy_object_proxy.Proxy(_load) if lazy else _load()


_load_preimports()

