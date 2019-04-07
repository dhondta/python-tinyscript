### Description

Very basic script demonstrating how to include metadata and how it is rendered in the help message.

### Creation

```sh
$ tinyscript-new script --name metadata
$ gedit metadata.py

```

### Code

```python hl_lines="6 7 8 9 10"
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from tinyscript import *


__author__    = "John Doe"
__email__     = "john.doe@example.com"
__version__   = "1.0"
__examples__  = [""]
__doc__       = "This script prints a simple 'Hello world !'"


if __name__ == '__main__':
    initialize(globals())
    logger.success("Hello world !")
```

### Help

```sh hl_lines="5 7"
$ python metadata.py -h
usage: metadata [-h] [-v]

Metadata v1.0
Author: John Doe (john.doe@example.com)

This script prints a simple 'Hello world !'

extra arguments:
  -h, --help     show this help message and exit
  -v, --verbose  verbose mode (default: False)

Usage examples:
  python metadata.py 

```

### Execution

```sh
$ python metadata.py 
12:34:56 [SUCCESS] Hello world !

```
