# Timing Feature

## Description

Very basic script demonstrating the execution timing feature.

## Code

```python hl_lines="7"
from tinyscript import *

if __name__ == '__main__':
    initialize(add_time=True)
    with Timer(timeout=1):
        while True:
            pass
    with Timer(timeout=2, fail_on_timeout=True):
        while True:
            pass
```

## Help

```sh
$ python step.py -h
Tool 

usage: python tool.py [-h] [--help] [--stats] [--timings] [-v]

extra arguments:
  -h             show usage message and exit
  --help         show this help message and exit
  -v, --verbose  verbose mode (default: False)

timing arguments:
  --stats    display execution time stats at exit (default: False)
  --timings  display time stats during execution (default: False)

```

## Execution

```sh hl_lines="1"
$ python tool.py --timings
12:34:56 [TIME] #0
12:34:57 [TIME] > Time elapsed: 1.00005912781 seconds
12:34:57 [TIME] > Time elapsed since execution start: 1.00027704239 seconds
12:34:57 [TIME] #1
12:34:59 [TIME] > Time elapsed: 2.00003600121 seconds
Traceback (most recent call last):
[...]
tinyscript.helpers.timeout.TimeoutError: Timer expired

```

!!! note "Timer expiration"
    
    The `TimeoutError` exception is raised because of `fail_on_timeout=True` in the second timer.

```sh hl_lines="1"
$ python tool.py --stats
Traceback (most recent call last):
[...]
tinyscript.helpers.timeout.TimeoutError: Timer expired
12:34:59 [TIME] Total time: 3.00039601326 seconds
#0
> 1.000041008 seconds
#1
> 2.00003600121 seconds

```
