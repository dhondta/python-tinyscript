# Usage

This section proposes a method for building a script/tool with Tinyscript.

Some example script/tools are available on the [GitHub repo](https://github.com/dhondta/tinyscript/tree/master/examples).


## Creation

A tiny tool is provided with the package to create a template instantly.

- **Create a tool**

```sh
$ tinyscript new test
```

This creates a script named `test.py` with minimal code.

??? example "`test.py`"

        :::python
        #!/usr/bin/env python
        # -*- coding: UTF-8 -*-
        from tinyscript import *
        # TODO: fill in imports


        __author__     = "John Doe"
        __email__      = "john.doe@example.com"
        __version__    = "1.0"
        __copyright__  = "J. Doe"
        __license__    = "agpl-3.0"
        #__reference__ = ""
        #__source__    = ""
        #__training__  = ""
        # TODO: fill in the docstring
        __doc__ = """
        This tool ...
        """
        # TODO: fill in examples
        __examples__ = [""]


        if __name__ == '__main__':
            # TODO: add arguments
            initialize()
            # TODO: write logic here

<br>

- **Create a PyBot tool**

```sh
$ tinyscript new test --target pybots.JSONBot
```

This creates a tool with a specific name and an import of particular class from the [PyBots library](https://github.com/dhondta/python-pybots).


## Customization

From there, the first thing to do can be to customize script/tool's metadata. For this purpose, the following constants can be tuned :

**Field** | **Comment**
--- | ---
```__author__``` | self-explanatory
```__copyright__``` | processed field for mentioning a copyright notice
```__credits__``` | list of contributors for displaying credits
```__details__``` | list of extra docstrings (for multi-level help)
```__doc__``` | script's docstring
```__docformat__``` | script's docstring styling format (`None`, `html`, `md`, `rst` or `textile`)
```__email__``` | self-explanatory
```__examples__``` | a list of strings providing example arguments and options (no need to mention the tool name)
```__license__``` | processed field for mentioning the license
```__reference__``` | raw text field for referencing a book/course/...
```__source__``` | same as for ```__reference__```
```__training__``` | raw text field for mentioning a training the script comes from
```__version__``` | self-explanatory

!!! note "Processed fields"
    
    Copyright is handled the following way: either a copyright text is specified or a 2-tuple with the copyright text and the starting year.
    
        :::python
        >>> from tinyscript import *
        >>> ts.copyright("test")
        '© 2020 test'
        >>> ts.copyright("test", 2019)
        '© 2019-2020 test'
    
    In a script, it is thus defined as a metadata field: `__copyright__ = "test", 2019`
    
    License is handled by a function that gets the full license name from its short name. For a list of short names, use:
    
        :::python
        >>> from tinyscript import *
        >>> ts.list_licenses()
        ['afl-3.0', 'agpl-3.0', ..., 'zlib']
    

!!! note "Comments & Sections"

    In both cases of a script or tool, comments with the *TODO* keyword are present in the template to indicate where the code should be adapted.

    When using a tool template (and not a script), some sections are defined for organizing the code in a standard way.


## Application

At this point, multiple global variables and modules imported by Tyniscript can be used to set script/tool's arguments and log messages in the code.


## Initialization

After customizing the metadata, the `initialize` function can be filled with the following arguments. The first list shows the utility features while the second one handles other tuning arguments.

**Argument** | **Purpose**
--- | ---
```sudo=[boolean]``` | Force privilege elevation at startup
```multi_level_debug=[boolean]``` | Set the verbose mode with multiple levels of logging (as shown hereafter).
```add_banner=[boolean]``` | Add a banner to be displayed when starting the script/tool.
```add_config=[boolean]``` | Add an option to input an INI configuration file.
```add_demo=[boolean]``` | Add the demonstration option (randomly picking an example).
```add_interact=[boolean]``` | Add an interaction option.
```add_progress=[boolean]``` | Add an option to show a progress bar.
```add_step=[boolean]``` | Add a stepping mode option, for setting breakpoints into the code by using the `step` function or the `Step` context manager.
```add_time=[boolean]``` | Add an execution timing option, for benchmarking the exeuction by using the `get\_time` and `get\_time\_since\_last` functions or the `Timer` context manager.
```add_version=[boolean]``` | Add the version option.
```add_wizard=[boolean]``` | Add a wizard option for asking the user to input each value.
```report_func=[function]``` | Add report options (output format, title, stylesheet and filename) by setting a function (taking no argument) that will generate the report at the end of the execution of the script/tool.

**Argument** | **Purpose**
--- | ---
```action_at_interrupt="[string]"``` | Control the action when Ctrl+C is hit ; one of: `exit`|`continue`|`confirm`.
```ext_logging=[boolean]``` | Enable extended logging options.
```multi_level_debug=[boolean]``` | Enable multi-level debugging with `-v[v[v[v]]]`.
```noargs_action="[string]"``` | Add a behavior when no argument is input by the user, a value amongst "`demo`", "`help`", "`step`", "`version`" or "`wizard`".
```post_actions``` | Enable/disable post-actions after an interrupt (only for interrupt, when exiting, these actions are triggered anyway), that is, features that are handled when the script is ending (e.g. report generation, time statistics displaying, ...).
```short_long_help=[boolean]``` | Enable/disable short/long help (usage info with `-h` and full help with `--help`).
```sudo=[boolean]``` | Elevate privilege before running.

??? example 

        :::python
        initialize(add_demo=True,
                   add_step=True,
                   noargs_action="wizard",
                   report_func=make_report)

<br>


## Validation

Once the initialization is tuned, a validation can be set if necessary using the `validate` function. This takes 3- or 4-tuples for defining the validation items.

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

The `Report` class and its related objects can be used to represent a report.

!!! note "Raw-text report parsing"
    An helper function is available for converting a [WPScan-like](https://github.com/wpscanteam/wpscan) report to a list of element classes with their associated content or a `Report` instance and the parsed elements if the report objects are imported in the global scope.
    
    For instance, this code will output a list of 2-tuples in the form `("[element_class]", content)`.
    
        :::python
        >>> from tinyscript.helpers import report2objects
        >>> with open("wpscan.txt") as f:
                obj = report2objects(f.read())
        >>> obj
        [("Text", "..."), ...]
    
    While this code will output a `Report` instance with its elements.
    
        :::python
        >>> from tinyscript.helpers import report2objects
        >>> from tinyscript.report import *
        >>> with open("wpscan.txt") as f:
                obj = report2objects(f.read())
        >>> obj
        [<Text: text-1>, ...]

With the `Report` class, multiple output formats can be used to generate the report as explained in [this section](reporting.html#output-formats).

??? example 

        :::python
        from tinyscript.report import *
        
        report = Report(
            Title("My title", tag="h2"),
            Section("My first section", tag="h4"),
            Code("#!/bin/bash\necho 'hello'",  language="bash"),
            Section("My second section", tag="h4"),
            Text("A paragraph", size=11, color="blue"),
        )
        print(report.md())
        print(report.html())

<br>

If using the `report_func` argument of `initialize`, a report generation function must be defined. This function must take no argument and return a tuple of report objects in the order to be displayed in the final report.

??? example 

        :::python
        def make_report():
            global headers, data
            return (
                Title("My nice report"),
                Section("A first section"),
                Text("Some introduction text"),
                Section("A second section"),
                Table(headers, data),
                "This is a free text",
            )

<br>

A header and a footer can also be defined.

??? example 

        :::python
        def make_report():
            return (
                Header(center="Nice report"),
                Footer(),
                "This is a free text",
            )

<br>

