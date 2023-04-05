# Enhanced Modules

## `code`
    
Formerly a set of [helper functions](helpers.md), the followings have been attached to the `code` module, which is now preimported.
    
Code can be monkey-patched at runtime using multiple functions, depending on what should be patched and how. Note that some of the functions rely on the [`patchy`](https://github.com/adamchainz/patchy) module.
    
- `add_line`, `add_lines`, `insert_line`, `insert_line`: it allows to add line(s) at specific indices (starting from 0), before or after (using `after=True`).
- `delete_line`, `delete_lines`, `remove_line`, `remove_lines`: it allows to delete line(s) by index (starting from 0).
- `patch`: alias for `patchy.patch`, taking a function and a patch file's text as arguments.
- `replace`: wrapper for `patchy.replace`, handling multiple replacements at a time, either replacing whole function (like in original `replace`) or only parts of the code.
- `replace_lines`: for replacing specific lines in the code of a given function, specifying replacements as pairs of line index (starting from 0) and replacement text.
- `restore`: for restoring a function to its original code.
- `revert`: for reverting code to a previous version (up to 3 previous versions).
- `source`: for getting function's source code (shortcut for `patchy.api._get_source`).
- `unpatch`: alias for `patchy.unpatch`, taking a function and a previous patch file's text as arguments in order to revert the function to its previous version.

A context manager is also available:

- `Patch`: alias for `patchy.temp_patch`, taking a function in argument and a patch ; it patches the function in the context of the open code block and then restores the function at the end of this block.

-----

## `getpass`

`getpass` is enhanced with a new function:

- `getcompliantpass`: it relies on `getpass` and allows to enforce a policy on the input password defined as a dictionary with the following keys:

    - `allowed`: the allowed characters set, that can be defined according to some mask modifiers (defaults to `?l?L?d?s`,  that is, lower- and uppercase, digits and special characters)
    - `entropy`: the minimum number of entropy bits required (defaults to `32`)
    - `length`: a 2-tuple with the minimum and maximum lengths (defaults to `(8, 40)`)
    - `required`: the required characters set, defined like the `allowed` set, cannot contain a mask modifier that is not in the `allowed` set (defaults to `?l?L?d`)
    - `rules`: set of string modification rules, as of [defined here](helpers.html#useful-general-purpose-functions)
    - `wordlists`: a dictionary of wordlists with keys being the filenames and their values being the lists of potential locations where they can be found (defaults to `{'password.lst': ["./", "~/"], 'rockyou.txt': ["./", "~/"]}`)

!!! note "Password policy mask groups"
    
    A mask similar to this used in HashCat can be provided. The allowed groups are:
    
    - `d`: digits
    - `h`: lowercase hexadecimal
    - `H`: uppercase hexadecimal
    - `l`: lowercase letters
    - `L`: uppercase letters
    - `p`: printable characters
    - `s`: punctuation characters and whitespace

-----

## `hashlib`
    
`hashlib`, while imported with Tinyscript, is enhanced with additional functions so that these must not be rewritten in many applications, that is:

- `hash_file`: this hashes a file per block.
- `[hash]_file` (e.g. `sha256_file`): each hash algorithm existing in the native `hashlib` has a bound function for hashing a file (e.g. `md5` is a native function of `hashlib` and will then have `md5_file`).

-----

## `inspect`
    
`inspect` has also a few additional functions:

- `getcallermodule`: gets the module object of the caller function.
- `getmainframe`: gets the frame where `__name__` is "`__main__`".
- `getmainglobals`: gets the globals dictionary from the main frame.
- `getmainmodule`: gets the module object from the main frame.
- `getparentframe`: gets the first parent frame in the stack that has the given keyword-values.

-----

## `itertools`

`itertools` is extended with the following items:

- `product2`: this is an improvement of the original `product`, also handling generators
- `reset`: given a generator function decorated by `resettable`, this functions can reset a generator instantiated by this function
- `resettable`: decorator for registering the reference to the generator function and its arguments used to make a generator, then making resettable each generator made by this function
- `NonResettableGeneratorException`: specific exception for handling a generator not decorated by `resettable` thrown while trying to reset it with the `reset` function

-----

## `logging`

`logging` is slightly enhanced with a few things:

- `addLogLevel`: adds a custom log level (with a color).
- `bindLogger`: decorates a function or method to provide a logger (`self.logger` for a method, global `logger` for a function).
- `configLogger`: configures the given logger with an `InterceptionHandler` (for catching and re-displaying the last log record) and a `StreamHandler`, also installing it in `coloredlogs`.
- `delLevelName`: deletes a level from the registry by its name or integer.
- `delLogLevel`: deletes a log level, that is, its complete definition.
- `lastLogRecord`: displays the last log record.
- `nullLogger`: a ready-to-use null logger.
- `renameLogger`: renames a logger from an old to a new name.
- `setLogger` / `setLoggers`: sets respectively one or multiple loggers using Tinyscript's logger configuration.
- `setLoggingLevel`: sets a logging level to every logger matching the given patterns.
- `unsetLogger` / `unsetLoggers`: unsets respectively one or multiple loggers (removing them from the root `logging` dictionary).
- `InterceptionHandler`: handler that intercepts the last log record.
- `RelativeTimeColoredFormatter`: custom formatter for handling relative log times.
- `Std2Logger`: instantiates a file-like object to write to a logger instance.

-----

## `random`

`random` is slightly enhanced with a few new items:

- `randstr`: allows to generate a random string with a given length and alphabet
- `LFSR`: adds an implementation of the Linear-Feedback Shifting Register stream generator, with the possibility of recovering its parameters by setting a target and using the Berlekamp-Massey algorithm.
- `Geffe`: adds an implementation of the Geffe stream generator.

-----

## `re`

`re` is enhanced with some new (fully lazy) functions to generate strings from regular expression patterns:

- `randstr`: generates a single random string from the input regex
- `randstrs`: provides a generator of N random strings from the input regex
- `size`: computes the number of all possible strings from the input regex
- `strings`: generates all possible strings from the input regex

-----

## `shutil`

`shutil` is slightly enhanced with a new function for Python 2:

- `which`: compatibility function (already exists in Python 3) that determines the path to a program.

-----

## `string`

`string` is slightly enhanced with a few new functions:

- `shorten`: shortens a string, taking by default the terminal width, otherwise a length of 40 characters (unless user-defined), and using an end token (by default "`...`").
- `sort_natural`: sort a list of strings taking numbers into account (returns nothing)
- `sorted_natural`: return a list of strings taking numbers into account

-----

## `virtualenv`

`virtualenv`, while imported with Tinyscript, is enhanced with convenient functions for setting up a virtual environment.

- `activate(venv_dir)`: sets environment variables and globals as of `bin/activate_this.py` in order to activate the given environment.
- `deactivate()`: unsets the current environment variables and globals.
- `install(package, ...)`: uses Pip to install the given package ; "`...`" corresponds to the arguments and keyword-arguments that can be passed to Pip.
- `is_installed(package)`: indicates if the given package is installed in the environment.
- `list_packages()`: lists the packages installed in the environment.
- `setup(venv_dir, requirements)`: sets up a virtual environment to the given directory and installs the given requirements (either a requirements file or a list of packages).
- `teardown(venv_dir)`: deactivates and removes the given environment ; if no directory given, the currently defined one is handled.

