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
['argparse', 'base64', 'binascii', 'collections', 'hashlib', 'itertools', 'logging', 'os', 'random', 're', 'shutil', 'signal', 'string', 'sys', 'time']
```

In a script/tool, all these built-in modules are preimported with the line `from tinyscript import *`.

!!! note "Improvements to `hashlib`"
    
    `hashlib`, while imported with Tinyscript, is enhanced with additional functions so that these must not be rewritten in many applications, that is:
    
    - `hash_file`: this hashes a file per block.
    - `[hash]_file` (e.g. `sha256_file`): each hash algorithm existing in the native `hashlib` has a bound function for hashing a file (e.g. `md5` is a native function of `hashlib` and will then have `md5_file`).

-----

## Helper types

While adding `argparse` arguments to the parser, Tinyscript provides some useful type validation functions that can be used with the `type` keyword argument, namely (returning `ValueError` when the validation fails):

- `file_exists`: existing file path
- `files_list`: list of only existing file paths
- `files_filtered_list`: list of at least one existing file path (bad paths are filtered)
- `folder_exists`: existing folder
- `ints`: list of integers
- `neg_int`, `negative_int`, `neg_ints`, `negative_ints`: single negative integer or list of negative integers
- `pos_int`, `positive_int`, `pos_ints`, `positive_ints`: single positive integer or list of positive integers
- `ip_address`, `ip_address_list`: valid IP address (IPv4 or IPv6) or list of IP addresses ; returns the result of `ipaddress.ip_address`
- `ip_address_network`: valid IP address network (e.g. `192.168.1.0/24`) ; returns the result of `ipaddress.ip_network`
- `port_number`: valid port number
- `port_number_range`: valid list of port numbers, ranging from and to the given bounds

-----

## Advanced option clash resolution

When a developper writes a script/tool relying on Tyniscript, every argument or option defined will preceed the default arguments, e.g. `-h` or `--help`. Tinyscript will then add these after the developper-defined ones, then using `argparse`'s conflict resolution first trying with full option strings (e.g. `-v` and `--verbose`), then with the long option string only (`--verbose`). If a name collision occurs, some of the pre-defined arguments use prefixes or suffixes to resolve it so that they can still be parsed. The following lists give the mappings between pre-defined default option names and their resolved names if a collision occurs.


List of "*extra*" arguments and options:

**Option strings** | **Description** | **If strings clash**
:---: | :---: | :---:
`--demo` | start a demo of a random example | `--play-demo`
`-h`, `--help` | show the help message | `--show-help`
`--step` | stepping mode | `--step-mode`
`--version` | show program's version number `__version__` | `--show-version`
`-v`, `--verbose` | verbose mode | `--verbose-mode`
`-w`, `--wizard` | start a wizard | `--start-wizard`

List of "*interaction*" arguments and options:

**Option strings** | **Description** | **If strings clash**
:---: | :---: | :---:
`--interact` | interaction mode | `--interact-mode`
`--host` | remote interacting host | `--remote-host`
`--port` | remote interacting host | `--remote-port`

List of "*timing*" arguments and options:

**Option strings** | **Description** | **If strings clash**
:---: | :---: | :---:
`--stats` | time statistics display (at end) | `--time-stats`
`--timings` | timing display mode | `--timings-mode`

List of "*report*" arguments and options:

**Option strings** | **Description** | **If strings clash**
:---: | :---: | :---:
`--output` | report output format | `--report-output`
`--title` | report title | `--report-title`
`--css` | report stylesheet file | `--report-css`
`--theme` | report stylesheet theme (overridden by `--css`) | `--report-theme`
`--filename` | report filename | `--report-filename`

