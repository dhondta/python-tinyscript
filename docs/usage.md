This section proposes a method for building a script/tool with Tinyscript.

Some example script/tools are available on the [GitHub repo](https://github.com/dhondta/tinyscript/tree/master/examples).


## Creation

A tiny tool is provided with the package to create a template instantly.

- **Create a script**

```sh
$ tinyscript-new script
```

This creates a script named `script.py` with minimal code.

??? example "`script.py`"

        :::python
        #!/usr/bin/env python
        # -*- coding: UTF-8 -*-
        from tinyscript import *


        if __name__ == '__main__':
            parser.add_argument("", help="")
            # TODO: write new arguments
            initialize(globals())
            # TODO: use validate(globals(), ...) if necessary
            # TODO: write logic here

<br>

- **Create a tool**

```sh
$ tinyscript-new tool
```

This creates a script named `tool.py` with a bit more code, comments and placeholders.

- **Create a PyBot script/tool**

```sh
$ tinyscript-new script pybots.HTTPBot --name my-http-bot
$ tinyscript-new tool pybots.JSONBot --name my-json-bot
```

This creates a script/tool with a specific name and an import of particular class from the [PyBots library](https://github.com/dhondta/pybots).


## Customization

From there, the first thing to do can be to customize script/tool's metadata. For this purpose, the following constants can be tuned :

**Field** | **Comment**
--- | ---
```__author__``` | self-explanatory
```__email__``` | self-explanatory
```__examples__``` | a list of strings providing example arguments and options (no need to mention the tool name)
```__reference__``` | field for referencing a book/course/...
```__source__``` | same as for ```__reference__```
```__training__``` | field for mentioning a training the script comes from
```__version__``` | self-explanatory

!!! note "Comments & Sections"

    In both cases of a script or tool, comments with the *TODO* keyword are present in the template to indicate where the code should be adapted.

    When using a tool template (and not a script), some sections are defined for organizing the code in a standard way.


## Application

At this point, multiple global variables and modules imported by Tyniscript can be used to set script/tool's arguments and log messages in the code.


## Initialization

After customizing the metadata, the `initialize` function can be filled with the desired arguments :

**Argument** | **Purpose**
--- | ---
```sudo=[boolean]``` | Force privilege escalation at startup
```multi_debug_level=[boolean]``` | Set the verbose mode with multiple levels of logging (as shown hereafter).
```add_demo=[boolean]``` | Add the demonstration option (randomly picking an example).
```add_step=[boolean]``` | Add a stepping mode option, for setting breakpoints into the code by using the `step` function or the `Step` context manager.
```add_version=[boolean]``` | Add the version option.
```add_wizard=[boolean]``` | Add a wizard option for asking the user to input each value.
```noargs_action="[string]"``` | Add a behavior when no argument is input by the user, a value amongst "`demo`", "`help`", "`step`", "`version`" or "`wizard`".
```report_func=[function]``` | Add report options (output format, title, stylesheet and filename) by setting a function (taking no argument) that will generate the report at the end of the execution of the script/tool.

??? example 

        :::python
        initialize(globals(),
                   add_demo=True,
                   add_step=True,
                   noargs_action="wizard",
                   report_func=make_report,
        )

<br>

When not setting the multi-level logging, the verbose mode, when enabled, sets the logging level to `DEBUG` while when setting it, the logging level is set as follows :

**Option** | **Logging Level**
--- | ---
 | `ERROR`
`-v` | `WARNING`
`-vv` | `INFO`
`-vvv` | `DEBUG`


## Validation

Once the initialization is tuned, a validation can be set if necessary using the `validate` function. This also takes `globals()` as the first argument, like `initialize`, but then takes 3- or 4-tuples for defining the validation items.

    (argument_name, condition, error_message[, default_value])

- `argument_name`: self-explanatory, e.g. `'test'`
- `condition`: an error condition expression, with the argument name replaced by `' ? '`
- `error_message`: the message to be displayed when the error `condition` is matched
- `default_value`: self-explanatory ; when not set, a trigger on the `condition` will prevent the script from running, otherwise the script/tool will just display a warning and continue with the default value

??? example 

        :::python
        validate(globals(),
            ('int1', " ? == 1", "Integer must be 1"),
            ('int2', " ? == 1", "Integer should be 1", 1),
        )
    
    `int1=0` will make the script crash with the error message while and `int1=1`, `int2=0` will cause `int2=1` and display a warning before continuing.

<br>


## Exit handlers

Some exit handlers can also be tuned to properly handle the end of the execution. The following handlers are available :

**Handler** | **Purpose**
--- | ---
`at_gracefully_exit` | Executed when no error occurred (exit code 0)
`at_interrupt` | Executed when signal `SIGINT` is received, typically when the user hits CTRL+C
`at_terminate` | Executed when signal `SIGTERM` is received, i.e. when the execution was terminated by another process or from the OS
`at_exit` | Executed anyway ; i.e. it will always trigger `logging.shutdown()`


## Reporting

If using the `report_func` argument of `initialize`, a report generation function must also be defined. This function must take no argument and return a tuple of report objects in the order to be displayed in the final report. For this purpose, multiple classes are available :

**Class** | **Description**
--- | ---
`Title(t)` | Big bold title line, taking 1 argument : title's [t]ext
`Section(t)` | Bold section title line, taking 1 argument : section title's [t]ext
`Header(l,c,r)` | For setting the heading line on every page, taking 3 arguments : the [l]eft, [c]enter and [r]ight headers
`Footer(l,c,r)` | For setting the footer line, taking 3 arguments : the [l]eft, [c]enter and [r]ight footers ; center's default is the page numbering (format: `#page/#pages`)
`Text(t)` | Text paragraph, takin 1 argument : the [t]ext to be displayed as a paragraph
`Table(h,r)` | Simple table with headers, taking 2 arguments : a list of [h]eaders and a list of [r]ows with values

??? example 

        :::python
        def make_report():
            global headers, data
            return (
                Title("My nice report"),
                Header(center="Nice report"),
                Footer(),
                Section("A first section"),
                Text("Some introduction text"),
                Section("A second section"),
                Table(headers, data),
            )

<br>

