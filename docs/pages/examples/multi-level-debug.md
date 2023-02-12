# Multi-Level Debugging

## Description

Very basic script demonstrating the multi-level debug mode.

## Code

```python hl_lines="4"
from tinyscript import *

if __name__ == '__main__':
    initialize(multi_level_debug=True)
    logger.critical("This is always displayed")
    logger.error("This is always displayed")
    logger.warning("This is displayed with -v")
    logger.info("This is displayed with -vv")
    logger.debug("This is displayed with -vvv")
```

## Help

```sh hl_lines="8 9"
$ python multi-level-debug.py --help
Tool 

usage: python multi-level-debug.py [-h] [--help] [-v]

extra arguments:
  -h      show usage message and exit
  --help  show this help message and exit
  -v      verbose level (default: 0)
           NB: -vvv is the highest verbosity level

```

## Execution

```sh hl_lines="1"
$ python multi-level-debug.py
12:34:56 [CRITICAL] This is always displayed
12:34:56 [ERROR] This is always displayed
```

```sh hl_lines="1"
$ python multi-level-debug.py -v
12:34:56 [CRITICAL] This is always displayed
12:34:56 [ERROR] This is always displayed
12:34:56 [WARNING] This is displayed with -v
```

```sh hl_lines="1"
$ python multi-level-debug.py -vv
12:34:56 [CRITICAL] This is always displayed
12:34:56 [ERROR] This is always displayed
12:34:56 [WARNING] This is displayed with -v
12:34:56 [INFO] This is displayed with -vv
```

```sh hl_lines="1"
$ python multi-level-debug.py -vvv
12:34:56 [CRITICAL] This is always displayed
12:34:56 [ERROR] This is always displayed
12:34:56 [WARNING] This is displayed with -v
12:34:56 [INFO] This is displayed with -vv
12:34:56 [DEBUG] This is displayed with -vvv
```
