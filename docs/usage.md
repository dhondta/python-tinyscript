## Creation

A tiny tool is provided with the package to create a template instantly.

- Create a script

```sh
$ tinyscript-new script
```

By default, it creates a script named `script.py` with minimal code. This is the same as typing `tinyscript-new script`.

```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from tinyscript import *


if __name__ == '__main__':
    parser.add_argument("", help="")
    # TODO: write new arguments
    initialize(globals())
    # TODO: use validate(globals(), ...) if necessary
    # TODO: write logic here
```

- Create a tool

```sh
$ tinyscript-new tool
```

This creates a script named `tool.py` with a bit more code, comments and placeholders.

- Create a PyBots script/tool

```sh
$ tinyscript-new script pybots.HTTPBot
$ tinyscript-new tool pybots.JSONBot
```

This creates a script/tool with an import of particular class from the [PyBots library](https://github.com/dhondta/pybots).


## Customization



## Initialization




## Validation


## Exit handlers

