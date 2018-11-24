### Description

Very basic script, with no particular feature used.

### Creation

```sh
$ tinyscript-new script --name simple-script
$ gedit simple-script.py

```

### Code

```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from tinyscript import *


if __name__ == '__main__':
    parser.add_argument("string", help="string to be displayed")
    initialize(globals())
    logger.info(args.string)
```

### Help

```sh
$ python simple-script.py -h
usage: simple-script [-h] [-v] string

SimpleScript

positional arguments:
  string         string to be displayed

extra arguments:
  -h, --help     show this help message and exit
  -v, --verbose  verbose mode (default: False)

```

### Execution

```sh
$ python simple-script.py "Hello World!"
12:34:56 [INFO] Hello World!

```
