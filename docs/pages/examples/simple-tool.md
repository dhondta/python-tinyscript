# Simple Tool

## Description

Very basic tool, using the demonstration feature when no argument is given. It also redefines a constant for tuning the logging.

## Code

```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = "John Doe"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__reference__ = "John's Blog (http://blogsite.com/john/)"
__doc__ = """
This tool is a simple example from the Tinyscript project.
"""
__examples__ = ["\"Hello World!\"", "\"Hello World!\" --critical"]

# --------------------- IMPORTS SECTION ---------------------
from tinyscript import *

# -------------------- CONSTANTS SECTION --------------------
DATE_FORMAT = "%Y"

# -------------------- FUNCTIONS SECTION --------------------
def hello(message, critical=False):
    (logger.info if not critical else logger.critical)(message)

# ---------------------- MAIN SECTION -----------------------
if __name__ == '__main__':
    parser.add_argument("message", help="message to be displayed")
    parser.add_argument("--critical", action="store_true", help="critical message")
    initialize(noargs_action="demo")
    hello(args.message, args.critical)
```

## Help

```sh
$ python simple-tool.py -h
SimpleTool v1.0
Author: John Doe
Reference: John's Blog (http://blogsite.com/john/)

This tool is a simple example from the Tinyscript project.

usage: python simple-tool.py [--critical] [-h] [--help] [-v] message

positional arguments:
  message        message to be displayed

optional arguments:
  --critical     critical message (default: False)

extra arguments:
  -h             show usage message and exit
  --help         show this help message and exit
  -v, --verbose  verbose mode (default: False)

Usage examples:
  python simple-tool.py "Hello World!"

```

## Execution

```sh
$ python simple-tool.py 
2018 [INFO] Hello World!

$ python simple-tool.py 
2018 [INFO] Hello World!

$ python simple-tool.py 
2018 [CRITICAL] Hello World!

```
