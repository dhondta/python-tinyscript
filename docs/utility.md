## Privilege elevation

This is achieved by passing a keyword argument `sudo=[boolean]` to `initialize(...)`.

```python hl_lines="3"
    ...
    initalize(...
              sudo=True,
              ...)
    ...
```

This will prompt the user for providing superuser credentials in case of insufficient privileges.

[See example here](examples/sudo.md)

-----

## Playing a demo

This is achieved by passing a keyword argument `add_demo=[boolean]` to `initialize(...)` and requires that `__examples__` is set as a non-empty list.

```python hl_lines="2 5"
...
__examples__ = ["test", "-sv", "-d --test"]
...
initalize(...
          add_demo=True,
          ...)
...
```

This adds the `--demo` option to pick a random example from `__examples__` and execute it.

[See example here](examples/demo.md)

-----

## Stepping the execution

This is enabled by passing a keyword argument `add_step=[boolean]` to `initialize(...)`.

```python hl_lines="3"
...
initalize(...
          add_step=True,
          ...)
...
```

From there, once the `--step` option is used in the command line, the script/tool pauses execution where a `step()` function or a `Step(...)` context manager is declared, waiting for the user to press a key and continue.

```python hl_lines="4 5 8 10"
...
def my_function(...):
    # do something
    step()
    with Step(at_end=True) as _:
        # this will stop after the execution of the block
...
with Step("this is a first step"):
    # do something
with Step("this is a second step"):
    # do something else
...
```

This adds the `--step` option to pause execution where `step`/`Step` is declared.

This feature is particularly useful when demonstrating a tool or when the execution can be split into steps whose execution must be triggered by the user.

[See example here](examples/step.md)

-----

## Timing the execution

This is achieved by passing a keyword argument `add_time=[boolean]` to `initialize(...)`. It will measure time in the script/tool where a `get_time()` or `get_time_since_last()` function or a `Timer(...)` context manager is used.

```python hl_lines="4 6 11 14 16"
...
def my_function(...):
    # do something
    get_time()
    # do something else
    with Timer(timeout=10):
        # this will measure time for this block of instructions
        # it will also stop block's execution after 10 seconds
...
initalize(...
          add_time=True,
          ...)
...
with Timer("First block with time measure"):
    # do something
with Timer("Second block with time measure"):
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

[See example here](examples/timing.md)

-----

## Displaying progress

This can be done by passing a keyword argument `add_progress=[boolean]` to `initialize(...)`. It will allow to display a progress bar where `progressbar` or `progress_manager` is used. This feature relies on the [`tqdm`](https://github.com/tqdm/tqdm) module.

```python hl_lines="3 6"
    ...
    initalize(...
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

```python hl_lines="3"
    ...
    initalize(...
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

```python hl_lines="3"
    ...
    initalize(...
              add_wizard=True,
              ...)
    ...
```

This adds the `--wizard` option for enabling the wizard mode.

-----

## Using a configuration INI file

This is achieved by passing a keyword argument `add_config=[boolean]` to `initialize(...)`. It will allow to read/write a configuration INI file with the arguments of the script. This can be useful for passing the right bunch of arguments in a saved file to a colleague or simply if you don't remember how to use your script with a complex configuration.

```python hl_lines="3"
    ...
    initalize(...
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

```python hl_lines="3"
    ...
    initalize(...
              add_version=True,
              ...)
    ...
```

This adds the `--version` option for displaying the version from `__version__`.

-----

## Action when no argument given

This is achieved by passing a keyword argument `noargs_action="[action]"` to `initialize(...)`. It triggers the related action when no argument is given by the user. It thus overrides the default behavior of argparse, which is to display an error message telling that too few arguments were given.

```python hl_lines="3"
    ...
    initalize(...
              noargs_action="...",
              ...)
    ...
```

!!! note "Available actions"

    It currently supports the following actions:
    
    - [`config`](#using-a-configuration-ini-file)
    - [`demo`](#playing-a-demo)
    - [`help`](#short-long-help)
    - [`interact`](#interacting-during-the-execution)
    - [`step`](#stepping-the-execution)
    - [`time`](#timing-the-execution)
    - [`usage`](#short-long-help)
    - [`version`](#adding-the-version-option)
    - [`wizard`](#starting-a-wizard)

-----

## Easy reporting (Python 3 only)

This is achieved by passing a keyword argument `report_func=[function]` to `initialize(...)`. It allows to trigger a user-provided report generation function which must use Tinyscript's report objects.

```python hl_lines="2 6 7 8 9 14"
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
    initalize(...
              report_func=make_report,
              ...)
    ...
```

This adds multiple options:

- `--output`: report output format (defaults to `pdf`, see [available formats here](usage.md))
- `--title`: report title
- `--css`: report stylesheet
- `--theme`: report theme (overridden by `--css`)
- `--filename`: report filename

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

!!! note "Action at interrupt"
    
    By default, when interrupting the execution, `sys.exit` is triggered therefore stopping the script. This behavior can be changed in several ways by setting `action_at_interrupt` when calling `initialize(...)`. The possible values are:
    
    - `confirm`: ask the user to confirm if the script should exit
    - `continue`: do not interrupt execution
    - `exit`: exit when SIGINT signal is sent

- *terminate*: before *exit*, if the script was terminated from the OS or due to an error
    
```python hl_lines="2"
...
def at_terminate():
    # do something before at_exit() if something went wrong
...
```

Some of these behaviors can be disabled in a block of code using the `DisableSignals` context manager by passing it the signal identifiers.

```python hl_lines="2"
...
with DisableSignals(SIGINT, SIGTERM) as _:
    # do something
    # if an interrupt or termination signal is raised, it will do nothing as
    #  long as we are in this block of code
...
```
