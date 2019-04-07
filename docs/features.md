## Metadata

Metadata can be defined at the very beginning of the script/tool and is used by Tinyscript to format the help message.

```python
from tinyscript import *

__author__    = "John Doe"
__email__     = "john.doe@example.com"
__version__   = "1.0"
__reference__ = "..."
__source__    = "..."
__training__  = "..."
__examples__  = ["..."]
__doc__       = "This tool ..."
__details__   = [
    """ ... """,
    """ ... """
]
...
```

This gives the following help message:

```sh hl_lines="4 5 6 7 8 10 17"
$ python tool.py -h
usage: tool [-h] [-v]

Tool v1.0
Author: John Doe (john.doe@example.com)
Reference: ...
Source: ...
Training: ...

This tool ...

optional arguments:
  -h, --help  show this help message and exit
  -v          debug verbose level (default: false)

Usage examples:
  python tool.py ...
```

[See example here](examples/metadata.md)

-----

## Privilege escalation

This is achieved by passing a keyword argument `sudo=[boolean]` to `initialize(...)`.

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              sudo=True,
              ...)
    ...
```

[See example here](examples/sudo.md)

-----

## Multi-level debugging

This is achieved by passing a keyword argument `multi_level_debug=[boolean]` to `initialize(...)`.

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              multi_level_debug=True,
              ...)
    ...
```

!!! note "Debug levels"

    This allows to change the behavior of the default argument `-v`/`--verbose` to:
    
    - '': `logging.ERROR`
    - `-v`: `logging.WARNING`
    - `-vv`: `logging.INFO`
    - `-vvv`: `logging.DEBUG`

[See example here](examples/multi-level-debug.md)

-----

## Multi-level help

This is achieved by setting the `__details__` metadata at the beginning of the script.

```python hl_lines="2 3 4 5"
    ...
    __details__ = [
    """Extra documentation, displayed when using -hh. """,
    """Other extra documentation, displayed when using -hhh. """
    ]
    ...
    initalize(globals(), ...)
    ...
```

!!! note "Help levels"

    This allows to change the behavior of the default argument `-h`/`--help` to:
    
    - `-h`: classical help message
    - `-hh`: classical help message + first string in __details__ list
    - `-hhh`: classical help message + first and second strings in __details__ list
    
    Note: Strings beyond the two first elements of `__details__` are not handled.

[See example here](examples/multi-level-help.md)

-----

## Playing a demo

This is achieved by passing a keyword argument `add_demo=[boolean]` to `initialize(...)` and requires that `__examples__` is set. Indeed, when using the `--demo` option, it will pick a random example and execute it.

```python hl_lines="2 7"
...
__examples__ = ["test", "-sv", "-d --test"]
...
    ...
    initalize(globals(),
              ...
              add_demo=True,
              ...)
    ...
```

[See example here](examples/demo.md)

-----

## Stepping the execution

This is achieved by passing a keyword argument `add_step=[boolean]` to `initialize(...)`. It will pause the script/tool where a `step()` function or a `Step(...)` context manager is used, if the user started the script/tool with `--step`.

```python hl_lines="4 5 11 14 16"
...
def my_function(...):
    # do something
    step()
    with Step(at_end=True) as _:
        # this will stop after the execution of the block
...
    ...
    initalize(globals(),
              ...
              add_step=True,
              ...)
    ...
    with Step("this is a first step") as step1:
        # do something
    with Step("this is a second step") as step2:
        # do something else
    ...
```

-----

## Timing the execution

This is achieved by passing a keyword argument `add_time=[boolean]` to `initialize(...)`. It will measure time in the script/tool where a `get_time()` or `get_time_since_last()` function or a `Timer(...)` context manager is used. If the user started the script/tool with `--stats` (or `--time-stats` if name collision), the timing statistics will be displayed at the end of the execution and if `--timings` (or `--timings-mode` if name collision) is used, timing information will be displayed where during the execution.

```python hl_lines="4 6 13 16 18"
...
def my_function(...):
    # do something
    get_time()
    # do something else
    with Timer(timeout=10) as timer:
        # this will measure time for this block of instructions
        # it will also stop block's execution after 10 seconds
...
    ...
    initalize(globals(),
              ...
              add_time=True,
              ...)
    ...
    with Timer("First block with time measure") as timer1:
        # do something
    with Timer("Second block with time measure") as timer2:
        # do something else
    ...
```

> - `get_time(message, start)`: This will measure time since execution start if no `start` value is provided. The default message displayed can be overwritten by setting `message`.
> - `get_time_since_last(message)`: This will measure time since the last measure (either through the use `Timer` or `get_time`/`get_time_since_last`). The default message displayed can be overwritten by setting `message`.
> - `Timer(description, message, timeout, fail_on_timeout)`: This will define a block where the execution time will be measured. A description can be given for display at the beginning of the block. The message can also be overwritten (displayed if the `--timings` option is used at execution). A timeout can be defined to force block's end and a flag can be defined to force `Timeout` exception when a timeout is raised.

-----

## Starting a wizard

This is achieved by passing a keyword argument `add_wizard=[boolean]` to `initialize(...)`. It will interactively ask for prividing arguments to the script/tool.

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              add_wizard=True,
              ...)
    ...
```

-----

## Adding the version option

This is achieved by passing a keyword argument `add_version=[boolean]` to `initialize(...)`. It provides an option to the script/tool for displaying the version from the metadata `__version__`.

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              add_version=True,
              ...)
    ...
```

-----

## Action when no argument given

This is achieved by passing a keyword argument `noargs_action="[action]"` to `initialize(...)`. It triggers the related action when no argument is given by the user. It thus overrides the default behavior of argparse, which is to display an error message telling that too few arguments were given.

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              noargs_action="...",
              ...)
    ...
```

!!! note "Available actions"

    It currently supports the following actions:
    
    - `config`
    - `demo`
    - `help`
    - `step`
    - `time`
    - `version`
    - `wizard`

-----

## Easy reporting (Python 3 only)

This is achieved by passing a keyword argument `report_func=[function]` to `initialize(...)`. It allows to add arguments related to report generation (e.g. `output`, `title` or `filename`) and triggers the given function which must use Tinyscript's report objects.

```python hl_lines="2 15"
...
def make_report():
    # define a list of headers here
    # process a list of data rows
    return (
        Title("Report title"),
        Header("", "Center heading line", ""),
        Footer(),  # will print the page number to the center of the footer
        Table(headers, rows),
    )
...
    ...
    initalize(globals(),
              ...
              report_func=make_report,
              ...)
    ...
```

-----

## Customizable exit handlers

Customized handlers can be defined for multiple events:

- *exit*: at the very end of the script/tool
    
```python hl_lines="2"
...
def at_exit():
    # do something at the very end of the script/tool
...
```
      
- *graceful exit*: before *exit*, if everything worked correctly

```python hl_lines="2"
...
def at_graceful_exit():
    # do something before at_exit() if execution succeeded
...
```
      
- *interrupt*: before *exit*, if the user interrupted the script/tool
    
```python hl_lines="2"
...
def at_interrupt():
    # do something before at_exit() if the user interrupted execution
...
```
      
- *terminate*: before *exit*, if the script was terminated from the OS or due to an error
    
```python hl_lines="2"
...
def at_terminate():
    # do something before at_exit() if something went wrong
...
```

