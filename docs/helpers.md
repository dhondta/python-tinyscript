## Useful general-purpose functions

According to the DRY philosophy, Tinyscript provides a few predefined utility functions:

**Name** | **Description**
:---: | :---:
`b` / `u` | Python2/3-compatible functions to convert to bytes or unicode
`byteindex` | Python2/3-compatible function to get the index of a byte
`capture` | decorator for capturing `stdout` and `stderr` of a function
`clear` | multi-platform clear screen function
`confirm` | Python2/3-compatible Yes/No input function (supporting style and palette, relying on [`colorful`](https://github.com/timofurrer/colorful)
`get_terminal_size()` | cross-platform terminal size function
`iterbytes` | Python2/3-compatible function to iterate bytes
`pause` | Python2/3-compatible dummy input function, waiting for a key to be pressed (supporting style and palette, relying on [`colorful`](https://github.com/timofurrer/colorful)
`silent` | decorator for silencing `stdout` and `stderr` of a function
`slugify` | slugify a string (handles unicode ; relying on [`slugify`](https://github.com/un33k/python-slugify))
`std_input` | Python2/3-compatible input function (supporting style and palette, relying on [`colorful`](https://github.com/timofurrer/colorful))
`timeout` | decorator for applying a timeout to a function
`user_input` | Python2/3-compatible enhanced input function (supporting style and palette, relying on [`colorful`](https://github.com/timofurrer/colorful), choices, default value and 'required' option)
`Capture` | context manager for capturing `stdout` and `stderr` of a code block
`Timeout` | context manager for applying a timeout to a code block
`TimeoutError` | custom exception for handling a timeout (as it is natively available in Python 3 but not in Python 2)

-----

## Extended `pathlib` classes

Tinyscript also provides 2 `pathlib`-related functions:

- `Path`: Extended Python2/3-compatible path class

    It fixes multiple compatibility issues between Python 2 and 3, namely `mkdir`'s `exist_ok` argument or methods `expanduser`, `read_text` and `write_text`.
    
    It also extends the class with multiple new useful methods like:
    
    - `append_bytes(data:bytes)`: appends bytes to the current file (complements `write_bytes`, which forces the `wb` mode)
    - `append_line(line:str)`: appends a newline (if not the beginning of the file) and `line`
    - `append_lines(*lines:str)`: appends multiple lines relying on `append_line(line)`
    - `append_text(data:str)`: appends text to the current file (complements `write_text`, which forces the `w` mode)
    - `choice(*filetypes:str)`: chooses a random file in the current folder among the given extensions (mentioning the dot ; e.g. `.py`)
    - `find(name:str, regex:bool)`: finds a file or folder, using `name` as a regex or not
    - `generate(prefix:str, suffix:str, length:int, alphabet:str)`: generates a random folder name (guaranteed to be non-existent) using the given prefix, suffix, length and alphabet, and returns the joined path
    - `is_hidden()`: checks whether the current file/folder is hidden
    - `is_samepath(other_path:str|Path)`: checks whether the given path is the same
    - `iterfiles()`: iterates over files only
    - `iterpubdir()`: iterates over visible directories only
    - `listdir(filter_func:lambda, sort:bool)`: list the current path based on a filter function, sorted or not
    - `reset()`: truncates the file
    - `remove()`: removes the current file or recursively removes the current folder
    - `walk(breadthfirst:bool, filter_func:lambda, sort:bool)`: walk the current path breadth-first or depth-first using a filter function, sorted or not
    
    It also adds some properties:
    
    - `basename`: dummy alias for `name`
    - `bytes`: returns file's content as raw bytes
    - `child`: returns the relative child path
    - `filename`: returns the complete filename (stem and suffix ; not natively present in `pathlib`)
    - `size`: returns path's size (recursively computed if it is a folder)
    - `text`: returns file's content as text

- `MirrorPath`: additional class for handling mirrored files and folders
    
    This mirrors an item, that is, if the given source does not exist in the given destination, it creates a symbolic link and recurses if it is a folder.
    
    - `mirror(source)`: mirrors the given source
    - `unmirror()`: removes the created symbolic links
    
    Basically, a path can be mirrored this way: `MirrorPath(destination, source)`. However, it can also be defined as `p = MirrorPath(destination)` and the `p.mirror(source)` method can then be used.

- `TempPath`: additional class for handling temporary folder
    
    This automatically creates a folder with a randomly generated name in OS' temporary location using a prefix, suffix, length and alphabet (like for `Path.generate(...)`).
    
    - `tempfile(**kwargs)`: passes `kwargs` to `tempfile.NamedTemporaryFile` and returns a temporary file descriptor under the current `TempPath` folder

-----

## Type checking functions

Tinyscript provides some type checking functions, for common data:

**Function** | **Description**
:---: | :---:
`is_bin` | binary string (with or without `\W` separators)
`is_dict` | dictionary
`is_dir` / `is_folder` | dummy shortcuts to `os.path.isdir`
`is_file` | dummy shortcut to `os.path.isfile`
`is_hash` | hash string, among MD5/SHA1/SHA224/SHA256/SHA512
`is_hex` | hexadecimal string (case insensitive)
`is_int` / `is_pos_int` / `is_neg_int` | integer (positive / negative)
`is_lambda` / `is_function` | lazy or any function
`is_list` | list, tuple, set
`is_md5` | MD5 hash
`is_sha1` | SHA1 hash
`is_sha224` | SHA224 hash
`is_sha256` | SHA256 hash
`is_sha512` | SHA512 hash
`is_str` | str, bytes, unicode

And for network-related data:

**Function** | **Description**
:---: | :---:
`is_defgw` | default gateway
`is_domain` | domain name
`is_email` | email address
`is_gw` | gateway
`is_ifaddr` | interface address
`is_ip` / `is_ipv4` / `is_ipv6` | IPv4 or IPv6 address
`is_mac` | MAC address
`is_netif` | network interface
`is_port` | port number

## Common argument types

While adding arguments to the parser (relying on `argparse`), Tinyscript provides some useful common type validation functions that can be used with the `type` keyword argument, namely (returning `ValueError` when the validation fails):

**Type** | **Output** | **Description**
:---: | :---: | :---:
`any_hash` | `str` | any valid hash amongst MD5|SHA1|SHA224|SHA256|SHA512
`file_exists` | `str` | existing file path
`files_list` | `lst(str)` | list of only existing file paths
`files_filtered_list` | `lst(str)` | list of at least one existing file path (bad paths are filtered)
`folder_exists` / `folder_exists_or_create` | `str` | existing folder or folder to be created if it does not exist
`ints` | `lst(int)` | list of integers
`md5_hash` | MD5 hash
`neg_int` / `negative_int` | `int` | single negative integer
`neg_ints` / `negative_ints` | `lst(int)` | list of negative integers
`pos_int` / `positive_int` | `int` | single positive integer
`pos_ints` / `positive_ints` | `lst(int)` | list of positive integers
`sha1_hash` | SHA1 hash
`sha224_hash` | SHA224 hash
`sha256_hash` | SHA256 hash
`sha512_hash` | SHA512 hash


And for network-related types:

**Type** | **Output** | **Description**
:---: | :---: | :---:
`default_gateway_address` | valid default gateway address
`domain_name` | valid domain name
`email_address` | valid email address
`gateway_address` | valid gateway address
`interface_address` | assigned interface address
`interface_address_list` | list of assigned interface addresses
`interface_address_filtered_list` | list of assigned interface addresses, with non-assigned ones filtered
`ip_address` / `ipv4_address` / `ipv6_address` | `IPAddress` | valid IP address (IPv4 or IPv6, in integer or string format)
`ip_address_list` / `ipv4_address_list` / `ipv6_address_list` | `generator(netaddr.IPAddress)` | list of IP addresses or networks (IPv4 or IPv6, in integer or string format)
`ip_address_network` / `ipv4_address_network` / `ipv6_address_network` | `generator(netaddr.IPAddress)` | valid IP address network in CIDR notation (e.g. `192.168.1.0/24`)
`mac_address` | `netaddr.EUI` | valid MAC address (integer or string)
`network_interface` | valid network interface on the current system
`port_number` | `int` | valid port number
`port_number_range` | `lst(int)` | valid list of port numbers, ranging from and to the given bounds

-----

## Data type tranformation functions

Tinyscript also provides a series of intuitive data transformation functions, formatted as follows:

```
[input_data_type_trigram]2[output_data_type_trigram]
```

The currently supported functions are:

- Binary <=> Integer: `bin2int` / `int2bin`

        :::python
        >>> bin2int("0100")
        4
        >>> int2bin(4, 4)
        '0100'
        >>> int2bin(4)
        '00000100'
        >>> bin2int("00000100 00000000", n_groups=2, order="big")
        4

        >>> int2bin(1024, sep=" ")
        '00000100 00000000'
        >>> int2bin(1024, n_groups=2, sep=" ", order="big")
        '00000000 00000100'
        >>> bin2int("0100 0000")
        1024
        >>> bin2int("00000100 00000000")
        1024
        >>> bin2int("0000010000000000", order="big")
        1024
        >>> bin2int("00000000 00000100", n_groups=2, order="big")
        1024

- Binary <=> Hexadecimal: `bin2hex` / `hex2bin`

        :::python
        >>> hex2bin("deadbeef", sep=" ")
        '11011110 10101101 10111110 11101111'
        >>> bin2hex("11011110 10101101 10111110 11101111")
        'deadbeef'

- Binary <=> String: `bin2str` / `str2bin`

        :::python
        >>> str2bin("test")
        '01110100011001010111001101110100'
        >>> str2bin("test", sep=" ")
        '01110100 01100101 01110011 01110100'

        >>> str2bin("test", 16, sep=" ")
        '0000000001110100 0000000001100101 0000000001110011 0000000001110100'
        >>> bin2str('1110100 1100101 1110011 1110100')
        'test'

- Integer <=> Hexadecimal: `int2hex` / `hex2int`

        :::python
        >>> hex2int("deadbeef")
        3735928559
        >>> int2hex(3735928559)
        'deadbeef'

        >>> int2hex(3735928559, 8)
        '00000000deadbeef'
        >>> hex2int("00000000deadbeef")
        3735928559

- Integer <=> String: `int2str` / `str2int`

        :::python
        >>> str2int("test")
        1952805748
        >>> int2str(1952805748)
        'test'

        >>> str2int("test string")
        140714483833450346658229863
        >>> int2str(140714483833450346658229863)
        'test string'

        >>> str2int("test string", 8)
        [8387236823645254770, 6909543]
        >>> int2str(8387236823645254770, 6909543)
        'test string'

- Hexadecimal <=> String: `hex2str` / `str2hex`

        :::python
        >>> str2hex("test string")
        '7465737420737472696e67'
        >>> hex2str("7465737420737472696e67")
        'test string'

-----

## Useful constants

Tinyscript also provides some predefined boolean constants:

**Name** | **Description**
:---: | :---:
`DARWIN` | Darwin platform
`JYTHON` | Java implementation of Python
`LINUX` | `Linux platform
`PYPY` | PyPy implementation of Python
`PYTHON3` | `True` if Python 3, `False` if Python 2
`WINDOWS` | Windows platform

-----

## Runtime monkey-patching functions

Code can be monkey-patched at runtime using multiple functions, depending on what should be patched and how. This feature relies on the [`patchy`](https://github.com/adamchainz/patchy) module.

The functions for this purpose are:

- `code_patch`: alias for `patchy.patch`, taking a function and a patch file's text as arguments.
- `code_unpatch`: alias for `patchy.unpatch`, taking a function and a previous patch file's text as arguments in order to revert the function to its previous version.
- `CodePatch`: context manager, alias for `patchy.temp_patch`, taking a function in argument and a patch ; it patches the function in the context of the open code block and then restores the function at the end of this block.
- `code_add_line`, `code_add_lines`, `code_insert_line`, `code_insert_line`: it allows to add line(s) at specific indices (starting from 0), before or after (using `after=True`).
- `code_delete_line`, `code_delete_lines`, `code_remove_line`, `code_remove_lines`: it allows to delete line(s) by index (starting from 0).
- `code_replace`: wrapper for `patchy.replace`, handling multiple replacements at a time, either replacing whole function (like in original `replace`) or only parts of the code.
- `code_replace_lines`: for replacing specific lines in the code of a given function, specifying replacements as pairs of line index (starting from 0) and replacement text.
- `code_restore`: for restoring a function to its original code.
- `code_revert`: for reverting code to a previous version (up to 3 previous versions).
- `code_source`: for getting function's source code (shortcut for `patchy.api._get_source`).

-----

## Copyright and licenses

A few functions are available to handle copyright and licenses:

```
>>> from tinyscript.helpers.licenses import *
>>> copyright("John Doe")
'© 2019 John Doe'
>>> license("test")
'Invalid license'
>>> license("agpl-3.0")
'GNU Affero General Public License v3.0'
>>> list_licenses()
['afl-3.0', 'agpl-3.0', 'apache-2.0', 'artistic-2.0', 'bsd-2-clause',
 'bsd-3-clause', 'bsd-3-clause-clear', 'bsl-1.0', 'cc', 'cc-by-4.0',
 'cc-by-sa-4.0', 'cc0-1.0', 'ecl-2.0', 'epl-1.0', 'eupl-1.1', 'gpl',
 'gpl-2.0', 'gpl-3.0', 'isc', 'lgpl', 'lgpl-2.1', 'lgpl-3.0',
 'lppl-1.3c', 'mit', 'mpl-2.0', 'ms-pl', 'ncsa', 'ofl-1.1',
 'osl-3.0', 'postgresql', 'unlicense', 'wtfpl', 'zlib']
```
