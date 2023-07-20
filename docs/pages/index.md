# Introduction

Tinyscript aims to quickly prototype tools by sparing as much lines of code as possible and providing base features (especially useful for debugging or understanding the execution flow) like configured logging, preimports, stepping, timing and so forth.

The idea is to make creating tools as easy as this:

```sh
$ tinyscript new test && gedit test.py
```

Simply modifying the template to:

```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from tinyscript import *

__author__     = "John Doe"
__version__    = "1.0"

if __name__ == '__main__':
    parser.add_argument("string", help="string to be displayed")
    initialize()
    logger.info(args.string)
```

Will give the following:

```sh
$ python test.py --help
Test 1.0
Author   : John Doe

usage: python test.py [-h] [--help] [-v] string

positional arguments:
  string  string to be displayed


extra arguments:
  -h             show usage message and exit
  --help         show this help message and exit
  -v, --verbose  verbose mode (default: False)

$ python test.py "Hello World!"
01:02:03 [INFO] Hello World!
```

-----

## Setup

This library is available on [PyPi](https://pypi.python.org/pypi/tinyscript/) and can be simply installed using Pip:

```sh
pip install --user tinyscript
```

or

```sh
pip3 install --user tinyscript
```

-----

## Rationale

This library is born from the need of efficiently building tools without caring for redefining various things or rewritting/setting the same functionalities like logging or parsing of input arguments.

In the meantime, I personnally used this library many times to create tools for my daily job or during cybersecurity or programming competitions and it proved very useful when dealing with rapid development.

