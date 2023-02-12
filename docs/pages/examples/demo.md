# Demo Feature

## Description

Very basic script demonstrating the demonstration feature, adding an option to start a demo using one of the available examples defined in `__examples__`.

!!! note "No example provided"

    If `__examples__` is not defined or is en empty list, the `--demo` will simply not be available, even if `add_demo` is `True` in the `initialize` function.

## Code

```python hl_lines="3 7"
from tinyscript import *

__examples__ = ["", "--test"]

if __name__ == '__main__':
    parser.add_argument("--test", action="store_true", help="test argument")
    initialize(add_demo=True)
    logger.success("First example" if not args.test else "Second example")
```

## Help

```sh
$ python demo.py -h
usage: python demo.py [--test] [--demo] [-h] [--help] [-v]

```

## Execution

```sh hl_lines="1"
$ python demo.py --demo
12:34:56 [SUCCESS] First example
```

```sh hl_lines="1"
$ python demo.py --demo
12:34:56 [SUCCESS] Second example
```
