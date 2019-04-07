### Description

Very basic script demonstrating the multi-level debug mode.

### Creation

```sh
$ tinyscript-new script --name multi-level-debug
$ gedit multi-level-debug.py

```

### Code

```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from tinyscript import *


if __name__ == '__main__':
    initialize(globals(), multi_level_debug=True)
    logger.critical("This is always displayed")
    logger.error("This is always displayed")
    logger.warning("This is displayed with -v")
    logger.info("This is displayed with -vv")
    logger.debug("This is displayed with -vvv")
```

### Help

```sh
$ python multi-level-debug.py -h
usage: python multi-level-debug.py [-h] [-v]

MultiLevelDebug

extra arguments:
  -h, --help  show this help message and exit
  -v          verbose level (default: 0)
               NB: -vvv is the highest verbosity level

```

### Execution

```sh
$ python multi-level-debug.py
12:34:56 [CRITICAL] This is always displayed
12:34:56 [ERROR] This is always displayed
```

```sh
$ python multi-level-debug.py -v
12:34:56 [CRITICAL] This is always displayed
12:34:56 [ERROR] This is always displayed
12:34:56 [WARNING] This is displayed with -v
```

```sh
$ python multi-level-debug.py -vv
12:34:56 [CRITICAL] This is always displayed
12:34:56 [ERROR] This is always displayed
12:34:56 [WARNING] This is displayed with -v
12:34:56 [INFO] This is displayed with -vv
```

```sh
$ python multi-level-debug.py -vvv
12:34:56 [CRITICAL] This is always displayed
12:34:56 [ERROR] This is always displayed
12:34:56 [WARNING] This is displayed with -v
12:34:56 [INFO] This is displayed with -vv
12:34:56 [DEBUG] This is displayed with -vvv
```
