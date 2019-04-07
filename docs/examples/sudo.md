### Description

Very basic script demonstrating running a script with sudo.

### Creation

```sh
$ tinyscript-new script --name sudo
$ gedit sudo.py

```

### Code

```python hl_lines="7"
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from tinyscript import *


if __name__ == '__main__':
    initialize(globals(), sudo=True)
    logger.success("Do it as sudo !")
```

### Help

```sh
$ python sudo.py -h
usage: python sudo.py [-h] [-v]

Sudo

extra arguments:
  -h, --help     show this help message and exit
  -v, --verbose  verbose mode (default: False)

```

### Execution

```sh hl_lines="2"
$ python sudo.py
[sudo] password for user: 
12:34:56 [SUCCESS] Do it as sudo !

```
