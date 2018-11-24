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

This is achieved by passing a keyword argument `add_step=[boolean]` to `initialize(...)`. It will pause the script/tool where a `step()` function or a `Step(...)` context manager is used, if the user started the script/tool with `--step`.

```python hl_lines="4"
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

## Action when no argument given

This is achieved by passing a keyword argument `noargs_action="[action]"` to `initialize(...)`. It currently supports "`demo`", "`help`", "`step`", "`version`" or "`wizard`" and triggers the related action when no argument is given by the user. It thus overrides the default behavior of argparse, which is to display an error message telling that too few arguments were given.

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              noargs_action="...",
              ...)
    ...
```

-----

## Easy reporting

This is achieved by passing a keyword argument `report_func=[function]` to `initialize(...)`. It allows to add arguments related to report generation (e.g. `output`, `title` or `filename`) and triggers the given function which must use Tinyscript's report objects.

```python hl_lines="4"
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

