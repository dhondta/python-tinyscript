# Metadata

## Description

Very basic script demonstrating how to include metadata and how it is rendered in the help message.

## Code

```python hl_lines="3 4 5 6 7"
from tinyscript import *

__author__    = "John Doe"
__email__     = "john.doe@example.com"
__version__   = "1.0"
__examples__  = [""]
__doc__       = "This script prints a simple 'Hello world !'"

if __name__ == '__main__':
    initialize()
    logger.success("Hello world !")
```

## Help

```sh hl_lines="5 7"
$ python metadata.py -h
Tool 1.0
Author   : John Doe (john.doe@example.com)

This script prints a simple 'Hello world !'

usage: python metadata.py [-h] [--help] [-v]

extra arguments:
  -h             show usage message and exit
  --help         show this help message and exit
  -v, --verbose  verbose mode (default: False)

Usage example:
  python metadata.py

```

## Execution

```sh
$ python metadata.py
12:34:56 [SUCCESS] Hello world !

```
