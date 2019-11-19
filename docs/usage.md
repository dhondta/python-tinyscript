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
            initialize()
            # TODO: use validate(...) if necessary
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
```__details__``` | list of extra docstrings (for multi-level help)
```__doc__``` | script's docstring
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
```multi_level_debug=[boolean]``` | Set the verbose mode with multiple levels of logging (as shown hereafter).
```add_config=[boolean]``` | Add an option to input an INI configuration file.
```add_demo=[boolean]``` | Add the demonstration option (randomly picking an example).
```add_interact=[boolean]``` | Add an interaction option.
```add_step=[boolean]``` | Add a stepping mode option, for setting breakpoints into the code by using the `step` function or the `Step` context manager.
```add_time=[boolean]``` | Add an execution timing option, for benchmarking the exeuction by using the `get\_time` and `get\_time\_since\_last` functions or the `Timer` context manager.
```add_version=[boolean]``` | Add the version option.
```add_wizard=[boolean]``` | Add a wizard option for asking the user to input each value.
```ext_logging=[boolean]``` | Enable extended logging options.
```noargs_action="[string]"``` | Add a behavior when no argument is input by the user, a value amongst "`demo`", "`help`", "`step`", "`version`" or "`wizard`".
```report_func=[function]``` | Add report options (output format, title, stylesheet and filename) by setting a function (taking no argument) that will generate the report at the end of the execution of the script/tool.

??? example 

        :::python
        initialize(add_demo=True,
                   add_step=True,
                   noargs_action="wizard",
                   report_func=make_report,
        )

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

A `Report` and its elements can be used from within a script without using the `report_func` argument of `initialize`. With the `Report` class, multiple output formats are available:

**Format** | **Description**
--- | ---
`csv` | CSV holding the data input from the `Table` elements
`html` | HTML body gathering all report elements except `Footer` and `Header` ; note that no CSS is applied but styling can be tuned using the `style`, `size` and `color` arguments for some elements
`json` | JSON holding the data input from the `Table` elements
`md` | Markdown with all report elements except `Footer` and `Header`
`pdf` | PDF (file only) with all report elements ; styling is applied according to the same arguments than for the `html` format but a CSS can also be provided to tune the PDF report
`xml` | XML holding the data input from the `Table` elements

The report can be generated as an output text (`report.[format]()`) or file (`report.[format](text=False)` ; in this case, the report is named `report.[format]`).

Multiple report elements are available:

**Class** | **Description**
--- | ---
`Code(c)` | Code block, taking 1 argument: the [c]ode
`Table(d,c,r)` | Table with column and row headers, taking 3 arguments : a list of rows as the [d]ata, a list of [c]olumn headers and a list of [r]ow headers
`Text(t)` | Text paragraph, takin 1 argument : the [t]ext to be displayed as a paragraph
`Title(t)` | Big bold title line, taking 1 argument : title's [t]ext
`Section(t)` | Bold section title line, taking 1 argument : section title's [t]ext

!!! note "Element styling"
    
    All these elements, except `Table`, inherit from `Text` and can have styling arguments:
    
    - `Text`: font `size` (defaults to 12), font `style` (defaults to "`normal`"), font `color` (defaults to "`black`") and HTML `tag` (defaults to "`p`")
    - `Title`: font `style`, font `color` and HTML `tag` (defaults to "`h1`") ; the font size is defined by the HTML tag
    - `Section`: inherits from `Title` with another HTML `tag` (defaults to "`h2`")
    - `Code`: font `size`, font `style`, font `color` (defaults to "`grey`"), highlighted `language` (used with both the Markdown and HTML output formats) and highlighted `hl_lines` (only used with the Markdown output format) ; the tag is always "`pre`"


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

<br>

!!! note "Free text"

    Note that free text can also be used. In this case, it will be handled as Markdown when outputing Markdown or HTML.


If using the `report_func` argument of `initialize`, a report generation function must also be defined. This function must take no argument and return a tuple of report objects in the order to be displayed in the final report.

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

Two other report elements can be used to tune a PDF report:

**Class** | **Description**
--- | ---
`Header(l,c,r)` | For setting the heading line on every page, taking 3 arguments : the [l]eft, [c]enter and [r]ight headers
`Footer(l,c,r)` | For setting the footer line, taking 3 arguments : the [l]eft, [c]enter and [r]ight footers ; center's default is the page numbering (format: `#page/#pages`)

!!! note "Only applies to PDF output"

    The `Header` and `Footer` elements only set `top` and `bottom` CSS properties for use with PDF generation. These have thus no effect on other output formats.

??? example 

        :::python
        def make_report():
            return (
                Header(center="Nice report"),
                Footer(),
                "This is a free text",
            )

<br>

