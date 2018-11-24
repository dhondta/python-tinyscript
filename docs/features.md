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
...
```

This gives the following help message:

```sh
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

-----

## Privileged escalation

This is achieved by passing a keyword argument `sudo=[boolean]` to `initialize(...)`.

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              sudo=True,
              ...)
    ...
```

-----

## Multi-level debugging

This is achieved by passing a keyword argument `multi_debug_level=[boolean]` to `initialize(...)`.

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              multi_debug_level=True,
              ...)
    ...
```

> This allows to change the behavior of the default argument `-v`/`--verbose` to:
> 
>  - '': `logging.ERROR`
>  - `-v`: `logging.WARNING`
>  - `-vv`: `logging.INFO`
>  - `-vvv`: `logging.DEBUG`

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

-----

## Stepping the execution

This is achieved by passing a keyword argument `add_step=[boolean]` to `initialize(...)`. It will pause the script/tool where a `step()` function or `Step(...)` context manager has been used, if the user started the script/tool with `--step`.

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              add_wizard=True,
              ...)
    ...
```

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




- Add a wizard option (defaults to `False`)

> This allows to interactively ask the user for arguments.

    :param glob:              globals() instance from the calling script
    :param sudo:              if True, require sudo credentials and re-run
                               script with sudo
    :param multi_debug_level: allow to use -v, -vv, -vvv (adjust logging level)
                               instead of just -v (only debug on/off)
    :param add_demo:          add an option to re-run the process using a random
                               entry from the __examples__ (only works if this
                               variable is populated)
    :param add_step:          add an execution stepping option
    :param add_version:       add a version option
    :param add_wizard:        add an option to run a wizard, asking for each
                               input argument
    :param noargs_action:     action to be performed when no argument is input
    :param report_func:       report generation function
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

