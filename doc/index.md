## Introduction

Tinyscript aims to quickly prototype scripts or tools by sparing as much lines of code as possible and providing useful base features like preimports and logging.

The idea is to make creating scripts/tools as easy as this:

```sh
$ tinyscript-new
$ gedit script.py
```

Simply modifying the template to:

```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from tinyscript import *


if __name__ == '__main__':
    parser.add_argument("string", help="string to be displayed")
    initialize(globals())
    logger.info(args.string)
```

Will give the following:

```sh
$ python script.py -h
usage: script [-h] [-v] string

Script

positional arguments:
  string      string to be displayed

optional arguments:
  -h, --help  show this help message and exit
  -v          debug verbose level (default: false)

$ python script.py "Hello World!"
01:02:03 [INFO] Hello World!
```

-----

## Rationale

This library is born from the need of quickly building efficient scripts and tools without caring for re-defining the same imports and variables (i.e. a parser with the `argparse` module or a logger with the `logging` module). The aim was also to provide standardly-formatted usage docstrings built from as few line codes as possible, i.e. by defining `__[...]__` metadata in the script/tool.

In the meantime, I personnally used this library many times to create scripts/tools for my job or during cybersecurity or programming competitions and it proved very useful when it comes to sparing time.

-----

## Definitions

In the remainder of this documentation, the following terms are used:

- **Script**: Simple code, as slight as possible.

- **Tool**: More complete code, with metadata and comments, heavier than a *Script*.
