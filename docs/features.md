## Metadata

Metadata can be defined using *dunders* (double underscore variables) at the very beginning of the script/tool and is used by Tinyscript to format the help message.

```python
from tinyscript import *

__author__    = "John Doe"
__copyright__ = "© 2019 John Doe Inc."
__email__     = "john.doe@example.com"
__license__   = "AGPLv3"
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

This will prompt the user for providing superuser credentials in case of insufficient privileges.

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

This modifies the classical `-v`/`--verbose` option to `-v`/`-vv`/`-vvv`.

!!! note "Debug levels"

    - '': `logging.ERROR`
    - `-v`: `logging.WARNING`
    - `-vv`: `logging.INFO`
    - `-vvv`: `logging.DEBUG`

[See example here](examples/multi-level-debug.md)

-----

## Extended logging options

This is achieved by passing a keyword argument `ext_logging=[boolean]` to `initialize(...)`.

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              ext_logging=True,
              ...)
    ...
```

This adds multiple options:

- `-f`, `--logfile`: This sets the log filename for saving logging messages.
- `-r`, `--relative`: This sets the log timestamps to the time relative to the start of the execution.
- `-s`, `--syslog`: This allows to save the log messages to `/var/log/syslog` (Linux only).

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

This modifies the classical `-h`/`--help` option to `-h`/`-hh`/`-hhh`.

!!! note "Help levels"

    - `-h`: classical help message
    - `-hh`: classical help message + first string in __details__ list
    - `-hhh`: classical help message + first and second strings in __details__ list
    
    Note: Strings beyond the two first elements of `__details__` are not handled by purpose.

[See example here](examples/multi-level-help.md)

-----

## Playing a demo

This is achieved by passing a keyword argument `add_demo=[boolean]` to `initialize(...)` and requires that `__examples__` is set as a non-empty list.

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

This adds the `--demo` option to pick a random example and execute it.

[See example here](examples/demo.md)

-----

## Stepping the execution

This is achieved by passing a keyword argument `add_step=[boolean]` to `initialize(...)`. It will allow to pause the script/tool where a `step()` function or a `Step(...)` context manager is used when the step mode is enabled.

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

This adds the `--step` option to enable the step mode.

-----

## Timing the execution

This is achieved by passing a keyword argument `add_time=[boolean]` to `initialize(...)`. It will measure time in the script/tool where a `get_time()` or `get_time_since_last()` function or a `Timer(...)` context manager is used.

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

This adds two options:

- `--stats`: The timing statistics will be displayed at the end of the execution.
- `--timings`: Timing information will be displayed where a timing function is called during the execution.

!!! note "Timing functions"
    
    - `get_time(message, start)`: This will measure time since execution start if no `start` value is provided. The default message displayed can be overwritten by setting `message`.
    - `get_time_since_last(message)`: This will measure time since the last measure (either through the use `Timer` or `get_time`/`get_time_since_last`). The default message displayed can be overwritten by setting `message`.
    - `Timer(description, message, timeout, fail_on_timeout)`: This will define a block where the execution time will be measured. A description can be given for display at the beginning of the block. The message can also be overwritten (displayed if the `--timings` option is used at execution). A timeout can be defined to force block's end and a flag can be defined to force `Timeout` exception when a timeout is raised.

-----

## Displaying progress

This can be done by passing a keyword argument `add_progress=[boolean]` to `initialize(...)`. It will allow to display a progress bar where `progressbar` or `progress_manager` is used. This feature relies on the [`tqdm`](https://github.com/tqdm/tqdm) module.

```python hl_lines="4 7"
    ...
    initalize(globals(),
              ...
              add_progress=True,
              ...)
    ...
    for i in progressbar(10):
        # do something
    ...
```

This adds the `--progress` option to enable the progress mode.

-----

## Interacting during the execution

This is achieved by passing a keyword argument `add_interact=[boolean]` to `initialize(...)`. It allows to interact with the program during its execution by spawning a Python interpreter. This feature relies on the built-in `code` module.

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              add_interact=True,
              ...)
    ...
```

This adds multiple options:

- `--interact`: Enable interaction mode.
- `--host`: Set a remote host for interacting. Defaults to 127.0.0.1.
- `--port`: Set a remote port for interacting. Defaults to 12345.

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

This adds the `--wizard` option for enabling the wizard mode.

-----

## Using a configuration INI file

This is achieved by passing a keyword argument `add_config=[boolean]` to `initialize(...)`. It will allow to read/write a configuration INI file with the arguments of the script. This can be useful for passing the right bunch of arguments in a saved file to a colleague or simply if you don't remember how to use your script with a complex configuration.

```python hl_lines="4"
    ...
    initalize(globals(),
              ...
              add_config=True,
              ...)
    ...
```

This adds two options:

- `-r`, `--read-config`: Filename of the INI file to be read for the input arguments.
- `-w`, `--write-config`: Filename of the INI file where the arguments of the current execution are to be written.

!!! note "If used as a `noarg_action`"
    
    When using this feature as an action when no argument is passed, `config.ini` is used as the default INI filename.

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

This adds the `--version` option for displaying the version from `__version__`.

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
    
    - [`config`](#using-a-configuration-ini-file)
    - [`demo`](#playing-a-demo)
    - [`help`](#multi-level-help)
    - [`interact`](#interacting-during-the-execution)
    - [`step`](#stepping-the-execution)
    - [`time`](#timing-the-execution)
    - [`version`](#adding-the-version-option)
    - [`wizard`](#starting-a-wizard)

-----

## Easy reporting (Python 3 only)

This is achieved by passing a keyword argument `report_func=[function]` to `initialize(...)`. It allows to trigger a user-provided report generation function which must use Tinyscript's report objects.

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

This adds multiple options:

- `--output`: report output format (defaults to `pdf`)
- `--title`: report title
- `--css`: report stylesheet
- `--theme`: report theme (overridden by `--css`)
- `--filename`: report filename

-----

## Patching code at runtime

Code can be modified at runtime using multiple functions, depending on what should be patched and how. This feature relies on the [`patchy`](https://github.com/adamchainz/patchy) module.

The functions for this purpose are:

- `code_patch`: alias for `patchy.patch`, taking a function and a patch file's text as arguments.
- `code_unpatch`: alias for `patchy.unpatch`, taking a function and a previous patch file's text as arguments in order to revert the function to its previous version.
- `code_replace`: wrapper for `patchy.replace`, handling multiple replacements at a time, either replacing whole function (like in original `replace`) or only parts of the code.
- `code_replace_lines`: for replacing specific lines in the code of a given function, specifying replacements as pairs of line index (starting from 0) and replacement text.
- `code_restore`: for restoring a function to its original code.
- `code_revert`: for reverting code to a previous version (up to 3 previous versions).

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

