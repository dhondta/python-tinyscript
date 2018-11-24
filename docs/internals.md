## Proxy parser

A parser that collects calls to an `argparse.ArgumentParser` so that, inside the tiny script/tool, a few lines of code can be spared by not redefining the `argparse.ArgumentParser` with its (long) parameters (e.g. the epilog).

```python hl_lines="3 5"
# normal script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=..., epilog=..., ...)
    parser.add_argument(...)
    args = parser.parse_args()
    ...
```

```python hl_lines="6"
# tiny script
from tinyscript import *
...
if __name__ == '__main__':
    parser.add_argument(...)
    initialize(globals())  # also does many other things than just parsing !
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
  -h, --help  show this help message and exit
  -v          debug verbose level (default: false)

Usage examples:
  python tool.py ...
```

-----

## Customizable initialization

This is achieved by passing arguments to `initialize(...)`. The first argument must always be `globals()` so that Tinyscript can populate the global scope of the script/tool.

Various features are handled by this initialization and are explained in the related section of this documentation.

-----

## Pre-configured colored logger

Tinyscript pre-configures a logger using the `logging` and [`coloredlogs`](https://github.com/xolox/python-coloredlogs) modules, immediately accessible in the global scope when `initialize` has been executed. If required, the logging format can be redefined.

```python hl_lines="4 5"
# normal script
import logging

logging.basicConfig(...)
logger = logging.getLogger(...)
...
```

```python hl_lines="9"
# tiny script
from tinyscript import *  # from this point, a logger is already setup
...
LOG_FORMAT  = "..."  # new format can be defined
DATE_FORMAT = "..."  # new format can be defined
...
if __name__ == '__main__':
    ...
    initialize(globals())  # the logger is then reconfigured with the new formats
```

-----

## Pre-imports

Some common built-in modules are preimported.

```sh
$ python
[...]
>>> from tinyscript import __preimports__
>>> __preimports__
['argparse', 'base64', 'binascii', 'collections', 'itertools', 'logging', 'os', 'random', 're', 'shutil', 'signal', 'string', 'sys', 'time']
```

In a script/tool, all these built-in modules are preimported with the line `from tinyscript import *`.

-----

## Advanced option clash resolution

When a developper writes a script/tool relying on Tyniscript, every argument or option defined will preceed the default arguments, e.g. `-h` or `--help`. Tinyscript will then add these after the developper-defined ones, then using argparse's conflict resolution first trying with full option strings (e.g. `-v` and `--verbose`), then with the long option string only (`--verbose`).

> Beware that, if every option string of a given argument or option is already set by the developper, this may break some features. For example, setting the `--output` option will prevent this of the report feature to be added, therefore preventing the user from setting the format of output.

List of default "*extra*" arguments and options:

**Option strings** | **Description**
:---: | :---:
`-d`, `--demo` | start a demo of a random example
`-h`, `--help` | show the help message

List of default "*report*" arguments and options:

**Option strings** | **Description**
:---: | :---:
`--output` | start a demo of a random example
`--title` | show the help message


