## Useful general-purpose functions

Tinyscript provides a few predefined utility functions:

**Name** | **Description**
:---: | :---:
`std_input` | Python2/3-compatible input function (supporting style and palette, relying on [`colorful`](https://github.com/timofurrer/colorful))
`user_input` | Python2/3-compatible enhanced input function (supporting style and palette, relying on [`colorful`](https://github.com/timofurrer/colorful), choices, default value and 'required' option)
`confirm` | Python2/3-compatible Yes/No input function (supporting style and palette, relying on [`colorful`](https://github.com/timofurrer/colorful)
`pause` | Python2/3-compatible dummy input function, waiting for a key to be pressed (supporting style and palette, relying on [`colorful`](https://github.com/timofurrer/colorful)
`slugify` | slugify a string (handles unicode ; relying on [`slugify`](https://github.com/un33k/python-slugify))
`b` / `u` | Python2/3-compatible functions to convert to bytes or unicode
`byteindex` | Python2/3-compatible function to get the index of a byte
`iterbytes` | Python2/3-compatible function to iterate bytes
`capture` | decorator for capturing `stdout` and `stderr` of a function
`Capture` | context manager for capturing `stdout` and `stderr` of a code block
`silent` | decorator for silencing `stdout` and `stderr` of a function
`get_terminal_size()` | cross-platform terminal size function
`timeout` | decorator for applying a timeout to a function
`Timeout` | context manager for applying a timeout to a code block
`TimeoutError` | custom exception for handling a timeout (as it is natively available in Python 3 but not in Python 2)

-----

## Type checking functions

According to the DRY philosophy, Tinyscript provides some type checking functions:

**Function** | **Description**
:---: | :---:
`is_int` / `is_pos_int` / `is_neg_int` | integer (positive / negative)
`is_dict` | dictionary
`is_list` | list, tuple, set
`is_str` | str, bytes, unicode
`is_lambda` / `is_function` | lazy or any function
`is_bin` | binary string (with or without `\W` separators)
`is_hex` | hexadecimal string (case insensitive)
`is_dir` / `is_folder` | dummy shortcuts to `os.path.isdir`
`is_file` | dummy shortcut to `os.path.isfile`
`is_ip` / `is_ipv4` / `is_ipv6` | IPv4 or IPv6 address
`is_mac` | MAC address
`is_port` | port number

## Common argument types

While adding arguments to the parser (relying on `argparse`), Tinyscript provides some useful type validation functions that can be used with the `type` keyword argument, namely (returning `ValueError` when the validation fails):

**Type** | **Output** | **Description**
:---: | :---: | :---:
`file_exists` | `str` | existing file path
`files_list` | `lst(str)` | list of only existing file paths
`files_filtered_list` | `lst(str)` | list of at least one existing file path (bad paths are filtered)
`folder_exists` / `folder_exists_or_create` | `str` | existing folder or folder to be created if it does not exist
`ints` | `lst(int)` | list of integers
`neg_int` / `negative_int` | `int` | single negative integer
`neg_ints` / `negative_ints` | `lst(int)` | list of negative integers
`pos_int` / `positive_int` | `int` | single positive integer
`pos_ints` / `positive_ints` | `lst(int)` | list of positive integers
`ip_address` / `ipv4_address` / `ipv6_address` | `IPAddress` | valid IP address (IPv4 or IPv6, in integer or string format)
`ip_address_list` / `ipv4_address_list` / `ipv6_address_list` | `generator(netaddr.IPAddress)` | list of IP addresses or networks (IPv4 or IPv6, in integer or string format)
`ip_address_network` / `ipv4_address_network` / `ipv6_address_network` | `generator(netaddr.IPAddress)` | valid IP address network in CIDR notation (e.g. `192.168.1.0/24`)
`mac_address` | `netaddr.EUI` | valid MAC address (integer or string)
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

Tinyscript also provides some predefined constants:

**Name** | **Description**
:---: | :---:
`LINUX` | `True` if Linux platform
`MACOS` | `True` if Mac OS platform
`WINDOWS` | `True` if Windows platform
`PYTHON3` | `True` if Python 3, `False` if Python 2

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
['afl-3.0', 'agpl-3.0', 'apache-2.0', 'artistic-2.0', 'bsd-2-clause', 'bsd-3-clause', 'bsd-3-clause-clear', 'bsl-1.0', 'cc', 'cc-by-4.0', 'cc-by-sa-4.0', 'cc0-1.0', 'ecl-2.0', 'epl-1.0', 'eupl-1.1', 'gpl', 'gpl-2.0', 'gpl-3.0', 'isc', 'lgpl', 'lgpl-2.1', 'lgpl-3.0', 'lppl-1.3c', 'mit', 'mpl-2.0', 'ms-pl', 'ncsa', 'ofl-1.1', 'osl-3.0', 'postgresql', 'unlicense', 'wtfpl', 'zlib']
```
