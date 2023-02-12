# Privilege Escalation

## Description

Very basic script demonstrating running a script with sudo.

## Code

```python hl_lines="4"
from tinyscript import *

if __name__ == '__main__':
    initialize(sudo=True)
    logger.success("Do it as sudo !")
```

## Help

```sh
$ python sudo.py -h
usage: python sudo.py [-h] [--help] [-v]

```

## Execution

```sh hl_lines="2"
$ python sudo.py 
[sudo] password for user: 
12:34:56 [SUCCESS] Do it as sudo !

```
