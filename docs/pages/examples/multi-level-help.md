# Multi-Level Help

## Description

Very basic script demonstrating the multi-level help messages.

## Code

```python hl_lines="7 8 9 10"
from tinyscript import *

__doc__ = "Main description"
__details__ = [
    "First level of details",
    "Second level of details",
]

if __name__ == '__main__':
    initialize()
```

## Help

```sh hl_lines="1 4"
$ python multi-level-help.py -h
Tool

Main description

usage: ./tool.py [-h] [-v]

extra arguments:
  -h             show extended help message and exit (default: 0)
                  NB: -hhh is the highest help detail level
  -v, --verbose  verbose mode (default: False)

```

```sh hl_lines="1 7"
$ python multi-level-help.py -hh
Tool
[...]
  -v, --verbose  verbose mode (default: False)


First level of details

```

```sh hl_lines="1 7 9"
$ python multi-level-help.py -hh
Tool
[...]
  -v, --verbose  verbose mode (default: False)


First level of details

Second level of details

```
