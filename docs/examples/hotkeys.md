# Hotkeys

## Description

Very basic script demonstrating the hotkeys feature.

## Code

```python hl_lines="3 4 5 6 7 9 10"
from tinyscript import *

HOTKEYS = ("default", {
    'p': ("TEST", logger.info),
    # this overrides the default handler for 'q' (for exiting)
    'q': lambda: q_handler(),
})

def q_handler():
    return "A computed string", logger.warning

if __name__ == '__main__':
    initialize()
    while True:
        pass
```

## Help

```sh
$ python hotkeys.py -h
usage: python hotkeys.py [-h] [--help] [-v]

```

## Execution

During this execution, the following keys are pressed: `p`, `q`, `l`, `i`, `Enter`, `i`, `y`, `Enter`.

```sh hl_lines="1"
$ python hotkeys.py 
12:34:56 [INFO] TEST
12:34:57 [WARNING] A computed string
12:34:58 [WARNING] A computed string
Do you really want to interrupt ? {(y)es|(n)o} [n] 
12:34:59 [WARNING] A computed string
Do you really want to interrupt ? {(y)es|(n)o} [n] y

```

From the default handlers:

- `l` displays the last log record again.
- `i` asks for interrupting the execution.
