# Step Feature

## Description

Very basic script demonstrating the execution stepping feature.

## Code

```python hl_lines="7"
from tinyscript import *

if __name__ == '__main__':
    initialize(add_step=True)
    step("Pause 1")
    print("First computation")
    with Step("Pause 2"):
        print("Second computation")
```

## Help

```sh
$ python step.py -h
usage: python step.py [-h] [--help] [--step] [-v]

```

## Execution

```sh hl_lines="1"
$ python step.py
First computation
Second computation

```

```sh hl_lines="1"
$ python step.py --step
12:34:56 [STEP] Pause 1
Press enter to continue
First computation
12:34:59 [STEP] Pause 2
Press enter to continue
Second computation

```
