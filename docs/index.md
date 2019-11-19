## Introduction

Tinyscript aims to quickly prototype scripts or tools by sparing as much lines of code as possible and providing base features (especially useful for debugging or understanding the execution flow) like configured logging, preimports, stepping, timing and so forth.

The idea is to make creating scripts/tools as easy as this:

```sh
$ tinyscript-new script --name "my-script"
$ gedit my-script.py
```

Simply modifying the template to:

```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from tinyscript import *


if __name__ == '__main__':
    parser.add_argument("string", help="string to be displayed")
    initialize()
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

This library is born from the need of quickly building efficient scripts and tools without caring for redefining various things or rewritting/setting the same functionalities like the logging or parsing of input arguments.

In the meantime, I personnally used this library many times to create scripts/tools for my job or during cybersecurity or programming competitions and it proved very useful when dealing with time constraints.

-----

## Definitions

In the remainder of this documentation, the following terms are used:

- **Script**: Simple code, as slight as possible, more suitable for a single or very specific use.

- **Tool**: More complete code, with metadata and comments, heavier than a *Script*, also aimed at being installed on a system.
