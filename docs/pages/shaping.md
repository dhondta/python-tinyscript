# Tool Shaping

## Metadata

Metadata can be defined using *dunders* (double underscore variables) at the very beginning of the script/tool and is used by Tinyscript to format the help message.

```python
from tinyscript import *

__author__       = "John Doe"
__contributors__ = [
    {'author': "James McAdams", 'email': "j.mcadams@hotmail.com"},
    {'author': "h4x0r1234", 'reason': "for his kind testing"},
]
__credits__      = "Thanks to Bob for his contribution"
__copyright__    = ("John Doe Inc.", 2020, 2023)
__description__  = "My Script"
__email__        = "john.doe@example.com"
__license__      = "agpl-3.0"
__version__      = "1.0"
__reference__    = "..."
__source__       = "..."
__training__     = "..."
__examples__     = ["..."]
__doc__          = "This tool ..."

initialize()
```

This gives the following help message:

```sh hl_lines="2 3 4 5 6 7 8 12 19"
$ python tool.py -h
My Script v1.0
Author      : John Doe (john.doe@example.com)
Contributors: James McAdams (j.mcadams@hotmail.com)
              h4x0r1234 - for his kind testing
Credits     : Thanks to Bob for his contribution
Copyright   : © 2020-2023 John Doe Inc.
License     : GNU Affero General Public License v3.0
Reference   : ...
Source      : ...
Training    : ...

usage: tool [-h] [-v]

This tool ...

extra arguments:
  -h             show usage message and exit
  --help         show this help message and exit
  -v, --verbose  verbose mode (default: False)

Usage examples:
  python tool.py ...
```

[See example here](examples/metadata.md)

For more detailed information about metadata fields, see [this section](usage.html#customization).

-----

## Package requirements checking

(only for Python3.8+)

Required module can be added via the `__requires__` dunder in order to check for requirements before the tool starts.

```python hl_lines="2 4"
...
__requires__  = {'tinyscript': "1.23"}
...
    initialize(...)
...
```

-----

## Help message styling

Help can be formatted using multiple markup languages for making the help text more user-friendly with colors and styling. This is configured by using the `__docformat__` dunder (which can also be `None`, meaning no formatting). This feature is supported by [`mdv`](https://github.com/axiros/terminal_markdown_viewer) and the theme can be tuned by using the constant `DOCFORMAT_THEME`.

Currently, the following markup languages are supported: HTML, Markdown, RestructuredText and Textile.

```python hl_lines="2 4"
...
__docformat__ = "html"  # None|"md"|"rst"|"textile"
...
DOCFORMAT_THEME = "Star"
...
```

!!! warning "Various formats support"
    
    The support for HTML, RestructuredText and Textile is based on document conversion with ['pypandoc'](https://pypi.org/project/pypandoc/) to get Markdown before using [`mdv`](https://github.com/axiros/terminal_markdown_viewer). In some cases with complex formate text, Pandoc can cause issues with indentation or break the layout. It is then advised to only use Markdown directly to avoid any conversion.

!!! note "List of themes"
    
    Unfortunately, the documentation of [`mdv`](https://github.com/axiros/terminal_markdown_viewer) is a bit poor. However, one can find the names of the available themes in [this JSON](https://github.com/axiros/terminal_markdown_viewer/blob/master/mdv/ansi_tables.json).

-----

## Script banner

Displaying a banner can be achieved in two ways:

- by passing a keyword argument `add_banner=True` ; in this case, a random font is used

```python hl_lines="3"
    ...
    initialize(...
               add_banner=True,
               ...)
    ...
```

- by defining the `BANNER_FONT` constant

The `BANNER_STYLE` constant also allows to style the banner with the following properties:

- `adjust`: can be `left` | `center` | `right` ; by default, the banner is centered
- `bgcolor`: determines the background color
- `fgcolor`: determines the foreground color

```python hl_lines="2 3"
...
BANNER_FONT = "roman"
BANNER_STYLE = {'adjust': "right", 'fgcolor': "blue"}
...
```

-----

## Multi-level debugging

This is achieved by passing a keyword argument `multi_level_debug=[boolean]` to `initialize(...)`.

```python hl_lines="3"
    ...
    initialize(...
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

```python hl_lines="3"
    ...
    initialize(...
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
    initialize(...)
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

## Short/Long help

This is enabled by the `short_long_help` parameter of `initialize(...)` and is set to `True` by default.

```python hl_lines="3"
...
initialize(...
          short_long_help=False,
          ...)
...
```

When set to `True`, `-h` only displays usage information and `--help` shows the full help message. If `False`, `-h` and `--help` both displays the full help message.

-----

## Argument groups ordering

Groups can be ordered by using the `after` and `before` keyword-arguments in `add_argument_group`.

```python hl_lines="2"
...
parser.add_argument_group("custom arguments", before="extra arguments")
...
```

-----

## Subparser choices sorted per category

When defining subparsers under the main parser, it is possible to use the "`category`" keyword to set a category to get the subparser sorted in. This allows, when there are lots of choices, to sort them and enhance readability of the help message.


```python hl_lines="3 4"
...
cmds = parser.add_subparsers(dest="command", metavar="CMD", title="positional argument", description="command to be executed")
cmd1 = cmds.add_parser("command1", category="category1", help="this does something")
cmd2 = cmds.add_parser("command2", category="category2", help="this does something")
initialize()
...
```

This examples will yield a help message that proposes "`CMD`", the *command to be executed*, with *category1* holding *command1* and *category2* holding *command2*.

-----

## Automatic Bash auto-completion with `argcomplete`

Using the related option, auto-completion can be enabled using `argcomplete`. This only applies `argcomplete.autocomplete` to the parser once initialized with the `initialize(...)` function, meaning that setting up the script and the Bash console accordingly is required as documented on [the README of `argcomplete´](https://github.com/kislyuk/argcomplete).

In Bash:

```session
$ activate-global-python-argcomplete --user
```

Your script, let us say `test.py`:

```python hl_lines="2 5"
#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
...
parser.add_argument("test", choices=["a", "b", "c"])
initialize(autocomplete=True)
...
```

!!! note "`PATH`"
    
    `test.py` needs to be in a folder registered in the `PATH` environment variable.

In Bash:

```session
$ eval "$(register-python-argcomplete test.py)"
```

