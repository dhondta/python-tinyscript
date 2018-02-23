[![pypi](https://img.shields.io/pypi/v/tinyscript.svg)](https://pypi.python.org/pypi/tinyscript/)
[![python](https://img.shields.io/pypi/pyversions/tinyscript.svg)](https://pypi.python.org/pypi/tinyscript/)
[![license](https://img.shields.io/pypi/l/tinyscript.svg)](https://pypi.python.org/pypi/tinyscript/)

# TinyScript

This library is currently a very minimalistic module aimed to shorten and format the way a "self-contained" Python tool can be made. It is mostly based on a script template that was used for building some specific tools holding useful metadata. It is not aimed to provide helpers as many other libraries already do this.

NB: By "self-contained", it is meant that the script does not rely on relative libraries or any configuration or other file, only on Python installed libraries. Such a tool is thus contained in a single file. This is because it is more convenient for deploying its into an executable path.

## Installation

```
sudo pip install tinyscript
```

or

```
sudo pip3 install tinyscript
```


## Features

- Formats tool's help using ```argparse``` and script metadata
- Creates a logger and enables colored logging
- Reduce lines for defining input arguments and increase script readability
- Pre-imports some common built-in modules
- Customize exit/interrupt/terminate handlers


## Usage

Every customization MUST be declared <u>before</u> the ```initialize(globals())``` call. Once invoked, this function appends useful references to the script's dictionary of global variables.

### Customizing metadata

Metadata fields used in the documentation:

**Field** | **Comment**
:---: | :---:
```__author__``` | self-explanatory
```__email__``` | self-explanatory
```__examples__``` | a list of strings providing example arguments and options (no need to mention the tool name)
```__reference__``` | field for referencing a book/course/...
```__source__``` | same as for ```__reference__```
```__training__``` | field for mentioning a training the script comes from
```__version__``` | self-explanatory


### Customizing logging

Constants that can be overwritten:

**Name** | **Default**
:---: | :---:
```DATE_FORMAT``` | ```%H:%M:%S```
```LOG_FORMAT``` | ```%(asctime)s [%(levelname)s] %(message)s```


### Defining arguments

Import from TinyScript prevents from redefining a parser and the ```initialize(globals())``` call achieves arguments parsing so that it only remains to add new arguments in the main script.

NB: A ```verbose``` switch is built-in by default like follows and can be overwritten:

```
parser.add_argument("-v", dest="verbose", action="store_true",
                    help="debug verbose level (default: false)")
```

This switch can also be configured for counting `v`'s to set the debug level. In this case, append `multi_debug_level=True` to the `initialize` call.


### Pre-imported modules

List of pre-imported built-in modules:
- ```logging```
- ```os```
- ```random```
- ```re```
- ```signal```
- ```sys```
- ```time```


### Customizing the exit/interrupt/terminate handler

Handlers are defined as follows:

- `at_exit`: This is executed when the script ends, whatever the reason. This can be used e.g. for closing a socket.
- `at_graceful_exit`: This only runs if the script completed successfully. `at_exit` is executed afterwards.
- `at_interrupt`: This only runs when SIGINT signal is received, in other words, when Ctrl+C is hit. `at_exit` is executed afterwards.
- `at_terminate`: This only runs when SIGTERM signal is received, in other words, when another process kills the script. `at_exit` is executed afterwards.


## Example

Very simple example with no documentation and no handlers:

```py
""" hello-world.py """
#!/usr/bin/env python
from tinyscript import *

__author__ = "John Doe"
__version__ = "1.0"
__reference__ = "Tinyscript documentation"
__examples__ = ["-h"]

if __name__ == '__main__':
    initialize(globals())
    logger.info("Hello world !")
```

In a terminal, it gives:

```sh
$ python hello-world.py 
12:34:56 [INFO] Hello world !

$ python hello-world.py -h
usage: hello-world.py [-h] [-v]

HelloWorld v1.0
Author: John Doe
Reference: Tinyscript documentation

optional arguments:
  -h, --help  show this help message and exit
  -v          debug verbose level (default: false)

Usage examples:
  python hello-world.py -h

```


Example with documentation and handlers:

```py
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = "John Doe"
__email__ = "john.doe@example.com"
__version__ = "1.0"
__reference__ = "A great book !"
__examples__ = ["-v", "-i 0"]
__doc__ = "This is an example tool"

from tinyscript import *

def at_exit():
    logger.info("Shutting down...")

def at_graceful_exit():
    logger.info("Execution successful")

def at_interrupt():
    logger.warn("Interrupted")

def at_terminate():
    logger.warn("Terminated")

if __name__ == '__main__':
    global logger
    parser.add_argument("-i", dest="integer", type=int, default=-1,
                        help="an example integer (default: -1)")
    parser.add_argument("-k", dest="integer2", type=int, default=-1,
                        help="another example integer (default: -1)")
    initialize(globals(),  # this appends 'args' and 'logger' to globals
               sudo=False, # this allows to require for sudo or not
               multi_debug_level=False) 
               # if multi_debug_level=True, this allows to use -v, -vv, -vvv
                           #  no -v  => ERROR
                           #  -v     => WARNING
                           #  -vv    => INFO
                           #  -vvv   => DEBUG
    # two kinds of validation: without default => triggers exit ;
    #                          with default    => sets the default and continues
    validate(globals(),
        ("integer", " ? < 0", "Integer must be greater or equal to 0"),
        ("integer2", " ? < 0", "Same as for the other integer", 1000),
    )  # this will exit because of 'integer' whose default is -1
       # and will only give a warning for 'integer2' whose default is -1
    logger.info(args)
    logger.info("Hit Ctrl+C to leave...")
    while True:
        pass  # Ctrl+C will use at_interrupt()
              # at_exit() will then execute

# 'python example.py' will fail
# 'python example.py -i 0 -v' will show a warning for 'integer2' (because of -v)
# 'python example.py -i 0 -k 0' will work with no warning
```
