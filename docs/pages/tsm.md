# Tiny Scripts Manager (TSM)

## Generating new script from template

TSM allows to create a script from a [template](https://github.com/dhondta/python-tinyscript/blob/main/src/tinyscript/template.py) that follows the classical structure with imports, metadata, classes and functions, and the `__main__` block.

```sh
$ tsm new my-script

$ cat my-script.py 
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
```


## Adding or removing scripts source

Source URL's can be added to or removed from `[config_path_to_tinyscript]/sources.conf` with the commands hereafter. For instance in Linux, `config_path_to_tinyscript` is `~/.config/tinyscript/`.

```sh
$ tsm add-source https://example.com/sources.list
01:23:45 [INFO] Added source 'https://example.com/sources.list'

$ tsm remove-source https://example.com/sources.list
01:24:56 [INFO] Removed source 'https://example.com/sources.list'
```

The `--fetch` option can be used to try downloading the source list.

```sh
$ tsm add-source https://example.com/sources.list --fetch
01:34:56 [INFO] Fetching source 'https://example.com/sources.list'...
01:34:56 [ERROR] HTTPSConnectionPool(host='example.com', port=443): Max retries exceeded with url: /sources.list (Caused by NameResolutionError("<urllib3.connection.HTTPSConnection object at 0x7f923c1ba640>: Failed to resolve 'example.com' ([Errno -2] Name or service not known)"))
```


## Updating scripts inventory

Sources can be fetched for getting and caching URL's to scripts by using the `update` command.

```sh
$ tsm update
00:12:34 [INFO] Fetching source 'https://raw.githubusercontent.com/dhondta/python-tinyscript/main/docs/scripts.list'...
```


## Searching for scripts

The `search` command allows to search for scripts, supporting pattern searching. Additionally, the `--fetch` option (short option: `-f`) can be used to fetch metadata of the matching scripts.

```sh
$ tsm search stego --fecth
stegolsb
  URL   : https://gist.github.com/dhondta/d2151c82dcd9a610a7380df1c6a0272c/raw/3af56d3fb21cca1685657ca67ff38b3e2a33896d/stegolsb.py
  Source: https://raw.githubusercontent.com/dhondta/python-tinyscript/main/docs/scripts.list
  Info  :
    - Author   : Alexandre D'Hondt
    - Version  : 1.2
    - Copyright: © 2020-2023 A. D'Hondt
    - License  : GNU General Public License v3.0

stegopit
  URL   : https://gist.github.com/dhondta/30abb35bb8ee86109d17437b11a1477a/raw/87ba9ede5029e3a8dfccce4a8d36ffe4f11b8f04/stegopit.py
  Source: https://raw.githubusercontent.com/dhondta/python-tinyscript/main/docs/scripts.list
  Info  :
    - Author   : Alexandre D'Hondt
    - Version  : 1.4
    - Copyright: © 2019-2023 A. D'Hondt
    - License  : GNU General Public License v3.0

stegopvd
  URL   : https://gist.github.com/dhondta/feaf4f5fb3ed8d1eb7515abe8cde4880/raw/d87ed0dc3a1e00711094764d117feda5389d71df/stegopvd.py
  Source: https://raw.githubusercontent.com/dhondta/python-tinyscript/main/docs/scripts.list
  Info  :
    - Author   : Alexandre D'Hondt
    - Version  : 1.1
    - Copyright: © 2020-2023 A. D'Hondt
    - License  : GNU General Public License v3.0
```


## Installing script

A script can be installed using the `install` command given its name. In the case when a script name exists in multiple sources, the precedence goes to the first match given the order of sources in the `[config_path_to_tinyscript]sources.conf` file.

```sh
$ tsm install wlf
00:01:23 [INFO] Script 'wlf' installed
```

The `--force` option can be used to overwrite an existing script.

```sh
$ tsm install stegopit --force
00:12:34 [INFO] Script 'stegopit' updated
```

The source to intall the script from can be forced by specifying the `--source` option.

```sh
$ tsm install custom-script --source https://example.com/sources.list
01:23:45 [INFO] Script 'custom-script' installed
```

The file permissions mode can be set using the `--mode` option (default is `750`).

```sh
$ tsm install stegopvd --mode 770
12:34:56 [INFO] Script 'stegopvd' installed
```

