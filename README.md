# TinyScript

This library is currently a very minimalistic module aimed to shorten and format the way a "self-contained" Python tool can be made. It is mostly based on a script template that was used for building some specific tools holding useful metadata. It is not aimed to provide helpers as many other libraries already do this.

NB: By "self-contained", it is meant that the script does not rely on relative libraries or any configuration or other file, only on Python installed libraries. Such a tool is thus contained in a single file. This is because it is more convenient for deploying its into an executable path.


## Features

- Formats tool's help using argparse and script metadata
- Creates a logger and enables colored logging
- Reduce lines for defining input arguments and increase script lisibility


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

NB: A ```verbose``` switch is built-in like follows and can be overwritten:

```
parser.add_argument("-v", dest="debug", action="store_true",
                    help="debug verbose level (default: false)")
```


## Example

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

if __name__ == '__main__':
    global logger
    parser.add_argument("-i", dest="integer", type=int, default=1,
                        help="an example integer")
    parser.add_argument("-k", dest="integer2", type=int, default=2,
                        help="another example integer")
    initialize(globals())  # this appends 'args' and 'logger' to globals
    # two kinds of validation: without default => triggers exit ;
    #                          with default    => sets the default and continues
    validate(
        ("integer", " ? >= 0", "Integer must be greater or equal to 0"),
        ("integer2", " ? >= 0", "Same as for the other integer", 1000),
    )  # this will exit because of 'integer'
    logger.info(args)
```
