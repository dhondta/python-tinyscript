# Tinyscript Internals

## Proxy parser

This is a parser that collects calls to a common `argparse.ArgumentParser` so that, inside the tiny script/tool, a few lines of code can be spared by not redefining the `argparse.ArgumentParser` with its (long) parameters (e.g. the epilog).

Normal script :

```python hl_lines="3 5"
...
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=..., epilog=..., ...)
    parser.add_argument(...)
    args = parser.parse_args()
    ...
```

With Tinyscript :

```python hl_lines="5"
from tinyscript import *
...
if __name__ == '__main__':
    parser.add_argument(...)
    initialize()  # also does many other things than just parsing !
    ...
```

-----

## Pre-defined help formatting

While sparing lines of code due to not redefining a complete argument parser, Tinyscript uses a pre-defined help formatting based on metadata, making very easy to build a well-formatted script/tool in only a few lines of code.

Here is an example of help output:

```sh
$ python tool.py -h
usage: tool [-h] [-v]

Tool v1.0
Author: John Doe (john.doe@example.com)
Reference: ...
Source: ...
Training: ...

This tool ...

optional arguments:
  -h             show usage message and exit
  --help         show this help message and exit
  -v, --verbose  verbose mode (default: False)

Usage examples:
  python tool.py ...
```

!!! note "Short/long help"
    
    The default behavior of help options is that "`-h`" only gives usage information while "`--help`" provides the full help message. This can be disabled using a parameter, see [this section of the documentation](shaping.html#shortlong-help).

-----

## Customizable initialization

This is achieved by passing arguments to `initialize(...)`.

Various [shaping](shaping.md) and [utility](utility.md) features are handled by this initialization and are explained in the related sections of this documentation.

-----

## Pre-configured colored logger

Tinyscript pre-configures a logger using the [`logging`](https://docs.python.org/3/howto/logging-cookbook.html) and [`coloredlogs`](https://github.com/xolox/python-coloredlogs) modules, immediately accessible in the global scope when `initialize` has been executed. If required, the logging format can be redefined.

Normal script :

```python hl_lines="3 4"
import logging

logging.basicConfig(...)
logger = logging.getLogger(...)
...
```

With Tinyscript :

```python hl_lines="3 4 8"
from tinyscript import *  # from this point, a logger is already setup
...
LOG_FORMAT  = "..."  # new format can be defined
DATE_FORMAT = "..."  # new format can be defined
...
if __name__ == '__main__':
    ...
    initialize()  # the logger is then reconfigured with the new formats
```

-----

## Advanced option clash resolution

When a developper writes a script/tool relying on Tyniscript, every argument or option defined will preceed the default arguments, e.g. `-h` or `--help`. Tinyscript will then add these after the developper-defined ones, then using `argparse`'s conflict resolution first trying with full option strings (e.g. `-v` and `--verbose`), then with the long option string only (`--verbose`). If a name collision occurs, some of the pre-defined arguments use prefixes or suffixes to resolve it so that they can still be parsed. The following lists give the mappings between pre-defined default option names and their resolved names if a collision occurs.


List of "*extra*" arguments and options:

**Option strings** | **Description** | **If strings clash**
--- | --- | ---
`--demo` | start a demo of a random example | `--play-demo`
`-h`, `--help` | show the help message | `--show-help`
`--step` | stepping mode | `--step-mode`
`--version` | show program's version number `__version__` | `--show-version`
`-v`, `--verbose` | verbose mode | `--verbose-mode`
`-w`, `--wizard` | start a wizard | `--start-wizard`

List of "*interaction*" arguments and options:

**Option strings** | **Description** | **If strings clash**
--- | --- | ---
`--interact` | interaction mode | `--interact-mode`
`--host` | remote interacting host | `--remote-host`
`--port` | remote interacting host | `--remote-port`

List of "*timing*" arguments and options:

**Option strings** | **Description** | **If strings clash**
--- | --- | ---
`--stats` | time statistics display (at end) | `--time-stats`
`--timings` | timing display mode | `--timings-mode`

List of "*report*" arguments and options:

**Option strings** | **Description** | **If strings clash**
--- | --- | ---
`--output` | report output format | `--report-output`
`--title` | report title | `--report-title`
`--css` | report stylesheet file | `--report-css`
`--theme` | report stylesheet theme (overridden by `--css`) | `--report-theme`
`--filename` | report filename | `--report-filename`

-----

## Pre-imports

Some common built-in or popular modules are preimported. Some others are enhanced to provide additional features. This can be inspected using the `__imports__` dunder.

```sh
$ python
[...]
>>> from tinyscript import *
>>> pprint(__imports__)
{'bad': [],
 'enhanced': ['code', 'codecs', 'hashlib', 'logging', 'virtualenv'],
 'optional': ['bs4', 'fs', 'numpy', 'pandas', 'requests'],
 'standard': ['argparse',
              'ast',
              'base64',
              'binascii',
              'codecs',
              'collections',
              'configparser',
              'ctypes',
              'fileinput',
              'itertools',
              'os',
              'random',
              're',
              'shlex',
              'shutil',
              'signal',
              'string',
              'struct',
              'subprocess',
              'sys',
              'time',
              'types']}
```

In a script/tool, all these modules are preimported within the global namespace using the line `from tinyscript import *`.

Modules can be loaded within a script/tool using the `load(module, optional)` function. If setting `optional` to `False` (the default) and the module does not exist, the name will be appended to the `__imports__['bad']` list.

Modules can also be reloaded using `reload` (this of `importlib` for Python 3, and the native one in Python 2 as it does not exist in `importlib` for Python 2).

The modules in the `__imports__['enhanced']` list are the native ones enhanced with additional features. These are enumerated in the [enhancements](enhancements.md) section.

-----

## Virtual environment context

It is possible to manage a virtual environment from within the script using the `virtualenv` module or the `VirtualEnv` context manager. Each available function from the module can be accessed from a context manager instance.

```python hl_lines="2 4 6"
...
with VirtualEnv("venv", "requirements.txt") as venv:
    ...
    for package, version in venv.list_packages():
        ...
    venv.install("my-package")
    ...
```
