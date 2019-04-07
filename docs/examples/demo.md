### Description

Very basic script demonstrating the demonstration feature, adding an option to start a demo using one of the available examples defined in `__examples__`.

!!! note "No example provided"

    If `__examples__` is not defined or is en empty list, the `--demo` will simply not be available, even if `add_demo` is `True` in the `initialize` function.

### Creation

```sh
$ tinyscript-new script --name demo
$ gedit demo.py

```

### Code

```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from tinyscript import *


__examples__ = ["", "--test"]


if __name__ == '__main__':
    parser.add_argument("--test", action="store_true", help="test argument")
    initialize(globals(), add_demo=True)
    logger.success("First example" if not args.test else "Second example")
```

### Help

```sh
$ python demo.py -h
usage: python demo.py [--test] [--demo] [-h] [-v]

Demo

optional arguments:
  --test         test argument (default: False)

extra arguments:
  --demo         demonstrate a random example
  -h, --help     show this help message and exit
  -v, --verbose  verbose mode (default: False)

Usage examples:
  python demo.py 
  python demo.py --test

```

### Execution

```sh
$ python demo.py --demo
12:34:56 [SUCCESS] First example
```

```sh
$ python demo.py --demo
12:34:56 [SUCCESS] Second example
```
