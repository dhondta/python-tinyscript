### Description

Very basic script demonstrating the multi-level help messages.

### Creation

```sh
$ tinyscript-new script --name multi-level-help
$ gedit multi-level-help.py

```

### Code

```python hl_lines="7 8 9 10"
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from tinyscript import *


__doc__ = "Main description"
__details__ = [
    "First level of details",
    "Second level of details",
]


if __name__ == '__main__':
    initialize(globals())
```

### Help

```sh hl_lines="1 9 10"
$ python multi-level-help.py -h
usage: python multi-level-help.py [-h] [-v]

MultiLevelHelp

Main description

extra arguments:
  -h             show extended help message and exit (default: 0)
                  NB: -hhh is the highest help detail level
  -v, --verbose  verbose mode (default: False)

```

```sh hl_lines="1 13"
$ python multi-level-help.py -hh
usage: python multi-level-help.py [-h] [-v]

MultiLevelHelp

Main description

extra arguments:
  -h             show extended help message and exit (default: 0)
                  NB: -hhh is the highest help detail level
  -v, --verbose  verbose mode (default: False)

First level of details

```

```sh hl_lines="1 13 15"
$ python multi-level-help.py -hh
usage: python multi-level-help.py [-h] [-v]

MultiLevelHelp

Main description

extra arguments:
  -h             show extended help message and exit (default: 0)
                  NB: -hhh is the highest help detail level
  -v, --verbose  verbose mode (default: False)

First level of details

Second level of details

```
