## Useful constants and compatibility functions

Tinyscript provides some predefined boolean constants, handy in some use cases:

**Name** | **Description**
--- | ---
`DARWIN` | Darwin platform
`JYTHON` | Java implementation of Python
`LINUX` | `Linux platform
`PYPY` | PyPy implementation of Python
`PYTHON3` | `True` if Python 3, `False` if Python 2
`WINDOWS` | Windows platform

It also provides some other constants:

**Name** | **Description**
--- | ---
`ENCODING` | system encoding
`LANGUAGE` | system language code

It defines a `classproperty` decorator for setting a property to the class level.

It also defines a few compatibility/utility functions for working with the same code either in Python 2 or 3.

**Name** | **Description**
--- | ---
`b` | bytes conversion function, overloading `six.b` for a better compatibility
`byteindex` | selects the byte value from a string at the given index
`colored` | allows to color text in a similar way to [`termcolor.colored`](https://pypi.org/project/termcolor/) (which is NOT in Tinyscript's requirements) but relying on [`colorful`](https://pypi.org/project/colorful/) (which is in Tinyscript's requirements)
`ensure_binary` | identical to `six.ensure_binary`
`ensure_str` | similar to `six.ensure_str`
`ensure_unicode` | dummy alias for `six.text_type`, by analogy to `ensure_binary` and `ensure_unicode`
`execfile` | added in Python3 for backward-compatibility
`iterbytes` | iterates over the bytes of a string (trivial in Python3 but
`u` | alias for `six.u`

!!! warning "Global scope and the `ts` module"
    
    On the contrary of the other helpers presented on this page, these are imported **in the global scope** while the others are attached to a dynamic module called "`ts`" (for the sake of not flooding the scope) when using `from tinyscript import *`.
    
    However, the helpers hereafter can still be imported granularly by using a specific import, e.g.:
    
        :::python
        >>> from tinyscript.helpers.termsize import get_terminal_size
        >>> get_terminal_size()
        [...]

-----

## Useful general-purpose functions

According to the [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) philosophy, Tinyscript provides a few predefined user interaction functions:

**Name** | **Description**
--- | ---
`ts.clear` | multi-platform clear screen function
`ts.confirm` | Python2/3-compatible Yes/No input function (supporting style and palette, relying on [`colorful`](https://github.com/timofurrer/colorful)
`ts.notify` | shortcut to the `notification.notify` function of [`plyer`](https://github.com/kivy/plyer)
`ts.pause` | Python2/3-compatible dummy input function, waiting for a key to be pressed (supporting style and palette, relying on [`colorful`](https://github.com/timofurrer/colorful)
`ts.std_input` | Python2/3-compatible input function (supporting style and palette, relying on [`colorful`](https://github.com/timofurrer/colorful))
`ts.user_input` | Python2/3-compatible enhanced input function (supporting style and palette, relying on [`colorful`](https://github.com/timofurrer/colorful), choices, default value and 'required' option)

It also provides some simple execution functions:

**Name** | **Description**
--- | ---
`ts.apply` | convenience function for applying a list of functions to the given arguments and keyword-arguments
`ts.execute` | dummy alias for calling a subprocess and returning its STDOUT and STDERR
`ts.process` | decorator for turning a function into a process
`ts.processes_clean` | cleanup function for joining processes opened with `ts.process`
`ts.thread` | decorator for turning a function into a thread
`ts.threads_clean` | cleanup function for joining threads opened with `ts.thread`
 
It also provides some other utility functions:
 
**Name** | **Description**
--- | ---
`ts.BitArray` | slightly extended `BitArray` class from [`bitstring`](https://github.com/scott-griffiths/bitstring)
`ts.capture` | decorator for capturing `stdout` and `stderr` of a function
`ts.Capture` | context manager for capturing `stdout` and `stderr` of a code block
`ts.entropy` | computation function for the Shannon entropy of a string
`ts.entropy_bits` | computation function for the number of bits of entropy (i.e. for a password)
`ts.get_terminal_size` | cross-platform terminal size function
`ts.pad` | String padding function, supporting `ansic9.23`, `incremental`, `iso7816-4`, `pkcs5`, `pkcs7` and `w3c` algorithms
`ts.silent` | decorator for silencing `stdout` and `stderr` of a function
`ts.slugify` | slugify a string (handles unicode ; relying on [`slugify`](https://github.com/un33k/python-slugify))
`ts.stdin_pipe` | Python2/3-compatible iterator of STDIN lines
`ts.strings` | generator for yielding strings with a minimal length and characters in a given charset from a string buffer
`ts.strings_from_file` | same as `ts.strings` but yielding strings from a file
`ts.timeout` | decorator for applying a timeout to a function
`ts.Timeout` | context manager for applying a timeout to a code block
`ts.TimeoutError` | custom exception for handling a timeout (as it is natively available in Python 3 but not in Python 2)
`ts.unpad` | String unpadding function (complementary of `ts.pad`)
`ts.xor` | repeated XOR function, also allowing to apply an ordinal offset on XORed characters
`ts.xor_file` | XOR a file with a given key

A few utility functions related to bruteforcing are also available:

**Name** | **Description**
--- | ---
`ts.bruteforce` | generator for making strings using a given alphabet from a minimum to a maximum length
`ts.bruteforce_mask` | generator for bruteforcing according to a given mask (either a string or a list of alphabets per character position)
`ts.bruteforce_pin` | generator for bruteforcing a variable-length PIN code (by default, length is 4) starting with a public top-20 most common PIN values
`ts.bruteforce_re` | generator for bruteforcing according to a given regular expression
`ts.dictionary` | generator for parsing a dictionary, applying rules if provided
`ts.expand_mask` | string expansion function for computing a bruteforce mask
`ts.parse_rule` | rule parsing function, for checking if it is valid and returning a generator of transformation functions to apply to the input text

!!! note "Bruteforce mask groups"
    
    For `ts.bruteforce_mask` or `ts.expand_mask`, a mask similar to this used in HashCat can be provided. The available groups are:
    
    - `?*`: all ordinals (0 to 255)
    - `<`: left bracket derivates `([{<`
    - `>`: right bracket derivates `)]}>`
    - `c`: lowercase consonants
    - `C`: uppercase consonants
    - `d`: digits
    - `h`: lowercase hexadecimal
    - `H`: uppercase hexadecimal
    - `l`: lowercase letters
    - `L`: uppercase letters
    - `p`: printable characters
    - `s`: punctuation characters and whitespace
    - `v`: lowercase vowels
    - `V`: uppercase vowels

!!! note "Dictionary entry transformation rules"
    
    For `ts.dictionary` (`rules` keyword-argument holding a comma-separated list of rules) and `ts.parse_rule`, a rule chaining multiple operations can be provided. The available string operations are:
    
    - `a[]`: append
    - `p[]`: prepend
    - `c`: capitalize
    - `i`: identity
    - `l`: lowercase
    - `r`: reverse
    - `s`: swapcase
    - `t`: title
    - `u`: uppercase
    
    For instance, the following rules will produce:
    
    - `ru`: reverse uppercase string ; "`test`" becomes "`TSET`"
    - `sa[123]`: swapcase and append "`123`" ; "`Test`" becomes "`tEST123`"
    - `i,r,u`: identity then reverse then uppercase ; "`test`" will produce `["test", "tset", "TEST"]`

!!! warning "Playing with bruteforce regex"
    
    `bruteforce_re` uses `itertools.product` to generate the suite of strings from a list of "*tokens*", that is sets of characters or full expressions. For instance, regex `test[1-3]` will give the product `["t", "e", "s", "t", ["1", "2", "3"]]`, still to be lazily generated by `bruteforce_re` to `["test1", "test2", "test3"]`.
    
    While using a regular expression like `test[a-c]{1,3}` (that could be generated using the prefix "`test`" with `bruteforce(3, "abc")`), a token (that is, a set of possibilities) is fully generated from the minimum size 1 to the maximum size 3 for the `product`, that is `["a", "b", "c", "aa", "ab", "ac", "ba", ...]`. If using larger sets of characters in the regex (e.g. `\S` or `[a-zA-Z0-9-_]`), this can crash the system as the memory will not be able to sustain the generation of the sublist of the `product`.

-----

## Data structures

Some particular data structures are provided:

**Name** | **Description**
--- | ---
`ts.ClassRegistry` | special dictionary whose keys are (base) classes and values are lists of related subclasses (e.g. `{Base: [Sub1, Sub2]}`) ; subclasses can be accessed by using the base class name and the subclass name, e.g. `d["base", "sub1"]`
`ts.ExpiringDict(max_age, sort_by_time)` | dictionary with expiring keys ; configured using the `max_age` argument (by default `0` meaning no expiration) and `sort_by_time` (allowing to sort keys either by time, if set to `True`, or in alphabetical order)
`ts.PathBasedDict` | particular dictionary where the keys are defined like a path (a dictionary is created for each base) ; e.g. `d['path/to/key'] = ...` will give `{'path': {'to': {'key': ...}}}`

Also related to this, the following helper functions are provided:

**Name** | **Description**
--- | ---
`ts.merge_dictionaries` | useful function for merging two or more dictionaries, either updating the first input dictionary (if `new` is `False` ; this is the default) or creating a new one, also updating the resulting dictionary with the latest input dictionaries (if `update` is `True` ; this is the default) or not, dealing with the duplicate values (when iterable) by merging them (related to the `duplicates` boolean)

-----

## CLI layout objects

This package also provides some CLI layout objects:

**Name** | **Description**
--- | ---
`ts.BorderlessTable` | borderless table based on an input data matrix, either with a heading line or not (`header` keyword-argument) ; relies on [`terminaltables`](https://pypi.org/project/terminaltables/)
`ts.NameDescription` | indented name-description line, with optional details (`details` third positional argument) ; also relies on [`terminaltables`](https://pypi.org/project/terminaltables/)

-----

## Extended `pathlib` classes

Tinyscript also provides 2 `pathlib`-related functions:

- `ts.Path`: Extended Python2/3-compatible path class

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

- `ts.ConfigPath`: additional class for handling configuration files or folders
    
    This subclass of `Path` takes an `application` name and a `file` boolean as arguments and makes configuration items depending on the OS (e.g. on Windows, using `%APPDATA%` or on Linux, user's home folder). If `file` is `True`, then make a config file path, otherwise create a config folder.
    
- `ts.MirrorPath`: additional class for handling mirrored files and folders
    
    This mirrors an item, that is, if the given source does not exist in the given destination, it creates a symbolic link and recurses if it is a folder.
    
    - `mirror(source)`: mirrors the given source
    - `unmirror()`: removes the created symbolic links
    
    Basically, a path can be mirrored this way: `MirrorPath(destination, source)`. However, it can also be defined as `p = MirrorPath(destination)` and the `p.mirror(source)` method can then be used.

- `ts.TempPath`: additional class for handling temporary folder
    
    This automatically creates a folder with a randomly generated name in OS' temporary location using a prefix, suffix, length and alphabet (like for `Path.generate(...)`).
    
    - `tempfile(**kwargs)`: passes `kwargs` to `tempfile.NamedTemporaryFile` and returns a temporary file descriptor under the current `TempPath` folder

-----

## Type checking functions

Tinyscript provides some type checking functions, for common data:

**Function** | **Description**
--- | ---
`ts.is_bin` | binary string (with or without `\W` separators)
`ts.is_bool` | boolean
`ts.is_dict` | dictionary
`ts.is_dir` / `ts.is_folder` | dummy shortcuts to `os.path.isdir`
`ts.is_executable` | whether the given path has the execution flag
`ts.is_file` | dummy shortcut to `os.path.isfile`
`ts.is_hex` | hexadecimal string (case insensitive)
`ts.is_int` / `ts.is_pos_int` / `ts.is_neg_int` | integer (positive / negative)
`ts.is_list` | list, tuple, set
`ts.is_long_opt` | for an argument with the "`--option`" format
`ts.is_str` | str, bytes, unicode
`ts.is_short_opt` | for an argument with the "`-o`" format

For string-related data:

**Function** | **Description**
--- | ---
`ts.is_digits` | the given string has only digits
`ts.is_letters` | the given string has only letters
`ts.is_lowercase` | the given string has only lowercase characters
`ts.is_printable` | the given string has only printable characters
`ts.is_punctuation` | the given string has only punctuation characters
`ts.is_regex` | the given string can be parsed as a regular expression
`ts.is_uppercase` | the given string has only uppercase characters

!!! note "Character percentage threshold"
    
    These functions have all a `threshold` argument that defaults to `1.0`. It can be tuned to accept strings that are not fully consisting of the given alphabet.

Also for various objects:

**Function** | **Description**
--- | ---
`ts.is_class` | class definition (relying on `inspect.isclass`)
`ts.is_coroutine` | coroutine (relying on `inspect.iscoroutine`)
`ts.is_coroutinefunc` | coroutine function (relying on `inspect.iscoroutinefunction`)
`ts.is_frame` | frame object (relying on `types.FrameType`)
`ts.is_function` | any function (relying on `types.[Builtin]FunctionType`)
`ts.is_generator` | generator object (relying on `inspect.isgenerator`)
`ts.is_generatorfunc` | generator function (relying on `inspect.isgeneratorfunction`)
`ts.is_instance` | instance of `object` or a specific class
`ts.is_iterable` | iterable object (relying on `collections.Iterable`)
`ts.is_lambda` | lazy function (relying on `types.LambdaType`)
`ts.is_method` | method of an object (relying on `types.[Builtin]MethodType`)
`ts.is_module` | module object (relying on `types.ModuleType`)
`ts.is_type` | type definition

For config-related data:

**Function** | **Description**
--- | ---
`ts.is_ini` / `ts.is_ini_file` | INI configuration content/file
`ts.is_json` / `ts.is_json_file` | JSON configuration content/file
`ts.is_toml` / `ts.is_toml_file` | TOML configuration content/file
`ts.is_yaml` / `ts.is_yaml_file` | YAML configuration content/file (note: this uses `yaml.safe_load(...)`)

For hash-related data:

**Function** | **Description**
--- | ---
`ts.is_hash` | hash string, among MD5/SHA1/SHA224/SHA256/SHA512
`ts.is_md5` | MD5 hash
`ts.is_sha1` | SHA1 hash
`ts.is_sha224` | SHA224 hash
`ts.is_sha256` | SHA256 hash
`ts.is_sha512` | SHA512 hash

And for network-related data:

**Function** | **Description**
--- | ---
`ts.is_asn` | 2-byte or 4-byte AS number
`ts.is_defgw` | default gateway
`ts.is_domain` | domain name
`ts.is_email` | email address
`ts.is_gw` | gateway
`ts.is_hostname` | hostname
`ts.is_ifaddr` | interface address
`ts.is_ip` / `ts.is_ipv4` / `ts.is_ipv6` | IPv4 or IPv6 address ; integer addresses are supported
`ts.is_ipnet` / `ts.is_ipv4net` / `ts.is_ipv6net` | IPv4 or IPv6 network (i.e. in CIDR notation) ; integer addresses are supported
`ts.is_mac` | MAC address
`ts.is_netif` | network interface
`ts.is_port` | port number
`ts.is_url` | Uniform Resource Locator

## Common argument types

While adding arguments to the parser (relying on `argparse`), Tinyscript provides some useful common type validation functions that can be used with the `type` keyword argument, namely (returning `ValueError` when the validation fails):

**Type** | **Output** | **Description**
--- | --- | ---
`ts.file_does_not_exist` | `str` | non-existing file path
`ts.file_exists` | `str` | existing file path
`ts.files_list` | `list(str)` | list of only existing file paths
`ts.files_filtered_list` | `list(str)` | list of at least one existing file path (bad paths are filtered)
`ts.folder_does_not_exist` | `str` | non-existing folder
`ts.folder_exists` / `ts.folder_exists_or_create` | `str` | existing folder or folder to be created if it does not exist
`ts.ints` | `list(int)` | list of integers
`ts.neg_int` / `negative_int` | `int` | single negative integer
`ts.neg_ints` / `negative_ints` | `list(int)` | list of negative integers
`ts.pos_int` / `positive_int` | `int` | single positive integer
`ts.pos_ints` / `positive_ints` | `list(int)` | list of positive integers
`ts.regular_expression` | `str` | string that can be parsed as a regular expression
`ts.str_contains(alphabet, threshold)` | `str` | string that contains characters with a percentage of at least `threshold`
`ts.str_matches(pattern, flags)` | `str` | string that matches the given pattern with the given flags

For config-related types:

**Function** | **Description**
--- | ---
`ts.ini_config` | INI configuration file
`ts.json_config` | JSON configuration file
`ts.toml_config` | TOML configuration file
`ts.yaml_config` | YAML configuration file

For hash-related types:

**Type** | **Output** | **Description**
--- | --- | ---
`ts.any_hash` | `str` | any valid hash amongst MD5|SHA1|SHA224|SHA256|SHA512
`ts.md5_hash` | `str` | MD5 hash
`ts.sha1_hash` | `str` | SHA1 hash
`ts.sha224_hash` | `str` | SHA224 hash
`ts.sha256_hash` | `str` | SHA256 hash
`ts.sha512_hash` | `str` | SHA512 hash

And for network-related types:

**Type** | **Output** | **Description**
--- | --- | ---
`ts.as_number` | `int` or `str` | valid 2-byte or 4-byte AS number
`ts.default_gateway_address` | `str` | valid default gateway address
`ts.domain_name` | `str`  | valid domain name
`ts.email_address` | `str`  | valid email address
`ts.gateway_address` | `str`  | valid gateway address
`ts.hostname` | `str` | valid hostname
`ts.interface_address` | `str`  | assigned interface address
`ts.interface_address_list` | `list(str)`  | list of assigned interface addresses
`ts.interface_address_filtered_list` | `list(str)` | list of assigned interface addresses, with non-assigned ones filtered
`ts.ip_address` / `ts.ipv4_address` / `ts.ipv6_address` | `netaddr.IPAddress` | valid IP address (IPv4 or IPv6, in integer or string format)
`ts.ip_address_list` / `ts.ipv4_address_list` / `ts.ipv6_address_list` | `generator(netaddr.IPAddress)` | list of IP addresses or networks (IPv4 or IPv6, in integer or string format)
`ts.ip_address_network` / `ts.ipv4_address_network` / `ts.ipv6_address_network` | `generator(netaddr.IPAddress)` | valid IP address network in CIDR notation (e.g. `192.168.1.0/24`)
`ts.mac_address` | `netaddr.EUI` | valid MAC address (integer or string)
`ts.network_interface` | `str` | valid network interface on the current system
`ts.port_number` | `int` | valid port number
`ts.port_number_range` | `list(int)` | valid list of port numbers, ranging from and to the given bounds
`ts.url` | valid Uniform Resource Locator

-----

## Data type tranformation functions

Tinyscript also provides a series of intuitive data transformation functions, formatted as follows:

```
[input_data_type_trigram]2[output_data_type_trigram]

[input_data_type_trigram]s2[output_data_type_trigram]

[input_data_type_trigram]2[output_data_type_trigram]s
```

The currently supported functions are:

- Binary <=> Integer: `ts.bin`(`s`)`2int`(`s`) / `ts.int`(`s`)`2bin`(`s`)

        :::python
        >>> ts.bin2int("0100")
        4
        >>> ts.int2bin(4, nbits_out=4)
        '0100'
        >>> ts.int2bin(4)
        '00000100'
        >>> ts.bin2int("0000010000000000")
        1024
        >>> ts.bin2int("0000010000000000", order="little")
        4
        >>> ts.bins2int("00000000", "00000100")
        4
        >>> ts.int2bin(1024)
        '0000010000000000'
        >>> ts.int2bin(1024, order="little")
        '0000000000000100'
        >>> ts.int2bins(1024, order="little", n_chunks=2)
        ['00000000', '00000100']
        >>> ts.ints2bin(29797, 29556)
        '01110100011001010111001101110100'

- Binary <=> Hexadecimal: `ts.bin`(`s`)`2hex`(`s`) / `ts.hex`(`s`)`2bin`(`s`)

        :::python
        >>> ts.hex2bin("deadbeef")
        '11011110101011011011111011101111'
        >>> ts.hex2bins("deadbeef", len_in=2)
        ['11011110', '10101101', '10111110', '11101111']
        >>> ts.bin2hex("11011110101011011011111011101111")
        'deadbeef'
        >>> ts.hexs2bin("dead", "beef")
        '11011110101011011011111011101111'
        >>> ts.bins2hex("11011110", "10101101", "10111110", "11101111")
        'deadbeef'

- Binary <=> String: `ts.bin`(`s`)`2str`(`s`) / `ts.str`(`s`)`2bin`(`s`)

        :::python
        >>> ts.str2bin("test")
        '01110100011001010111001101110100'
        >>> ts.str2bin("test", nbits_out=16)
        '0000000001110100000000000110010100000000011100110000000001110100'
        >>> ts.bin2str('01110100011001010111001101110100')
        'test'

- Integer <=> Flags: `ts.int2flags` / `ts.flags2int`

        :::python
        >>> ts.int2flags(12)
        [True, True, False, False]
        >>> ts.flags2int([True, True, False, False])
        12

- Integer <=> Hexadecimal: `ts.int`(`s`)`2hex`(`s`) / `ts.hex`(`s`)`2int`(`s`)

        :::python
        >>> ts.hex2int("deadbeef")
        -559038737
        >>> ts.int2hex(3735928559)
        'deadbeef'
        >>> ts.int2hex(3735928559, 8)
        '00000000deadbeef'
        >>> ts.hex2int("00000000deadbeef")
        3735928559

- Integer <=> String: `ts.int`(`s`)`2str`(`s`) / `ts.str`(`s`)`2int`(`s`)

        :::python
        >>> ts.str2int("test")
        1952805748
        >>> ts.int2str(1952805748)
        'test'
        >>> ts.ints2str(29797, 29556)
        'test'
        >>> ts.str2int("test string")
        140714483833450346658229863
        >>> ts.int2str(140714483833450346658229863)
        'test string'
        >>> ts.str2int("test string", 8)
        [8387236823645254770, 6909543]
        >>> ts.int2str(8387236823645254770, 6909543)
        'test string'

- Hexadecimal <=> String: `ts.hex`(`s`)`2str`(`s`) / `ts.str`(`s`)`2hex`(`s`)

        :::python
        >>> ts.str2hex("test string")
        '7465737420737472696e67'
        >>> ts.hex2str("7465737420737472696e67")
        'test string'

- List <=> String: `ts.lst2str` / `ts.str2lst`

        :::python
        >>> ts.lst2str([1, 2, 3, 4])
        '1,2,3,4'
        >>> ts.lst2str([1, 2, 3, 4], sep="")
        '1234'
        >>> ts.str2lst("abc")
        ['a', 'b', 'c']
        >>> ts.str2lst("123")
        [1, 2, 3]

- Others: `ts.json2html` (relying on [`json2html`](https://pypi.org/project/json2html/)) / `ts.json2xml` (relying on [`dicttoxml`](https://pypi.org/project/dicttoxml/)) / `ts.xml2json`  (relying on [`xmltodict`](https://pypi.org/project/xmltodict/)) / `ts.report2objects` (transforms a WPScan-like report to a Tinyscript [`Report`](reporting.html#report))

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
