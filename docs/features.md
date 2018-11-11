## Script metadata and help formatting

Metadata can be defined at the beginning of the script and is used by Tinyscript to format the help message.

```python
from tinyscript import *

__author__    = "John Doe"
__email__     = "john.doe@example.com"
__version__   = "1.0"
__reference__ = "..."
__source__    = "..."
__training__  = "..."
__examples__  = ["..."]
__doc__       = "This tool ..."
...
```

This gives the following help message:

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

## Proxy parser

A parser that collects calls to an `argparse.ArgumentParser` so that, inside the tiny script/tool, a few lines of code can be spared by not redefining the `argparse.ArgumentParser` with its parameters (e.g. the epilog).

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

## Customized initialization

This is achieved by passing arguments to `initialize(...)`.

- Require `sudo`

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              sudo=True,
              ...)
    ...
```

- Configure multi-level debugging:

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              multi_debug_level=True,
              ...)
    ...
```

> This allows to change the behavior of the default argument `-v`/`--verbose` to:
> 
>  - '': `logging.ERROR`
>  - `-v`: `logging.WARNING`
>  - `-vv`: `logging.INFO`
>  - `-vvv`: `logging.DEBUG`

- Add a help message (defaults to `True`)
 
> This allows to format the help messages using the defined metadata variables.

- Add a demo option (defaults to `False`)

> This allows to play a random set of arguments as defined in `__examples__`.

- Add a wizard option (defaults to `False`)

> This allows to interactively ask the user for arguments.

-----

## Customized exit handlers

Customized handlers can be defined for multiple events:

- *exit*: at the very end of the script/tool
    
```python hl_lines="2"
...
def at_exit():
    # do something at the very end of the script/tool
...
```
      
- *graceful exit*: before *exit*, if everything worked correctly

```python hl_lines="2"
...
def at_graceful_exit():
    # do something before at_exit() if execution succeeded
...
```
      
- *interrupt*: before *exit*, if the user interrupted the script/tool
    
```python hl_lines="2"
...
def at_interrupt():
    # do something before at_exit() if the user interrupted execution
...
```
      
- *terminate*: before *exit*, if the script was terminated from the OS or due to an error
    
```python hl_lines="2"
...
def at_terminate():
    # do something before at_exit() if something went wrong
...
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
