#!/usr/bin/env python
# -*- coding: UTF-8 -*-


__all__ = ["new"]


SHEBANG = """#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
TOOL_METADATA = """__author__ = "Your name"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
#__reference__ = ""
#__source__ = ""
#__training__ = ""
# TODO: complete the docstring
__doc__ = \"\"\"
This tool ...
\"\"\"
# TODO: complete examples
__examples__ = [""]

"""
TOOL_SECTIONS = """# --------------------- IMPORTS SECTION ---------------------
{imports}# TODO: complete imports
# non-standard imports with warning if dependencies are missing
try:
    # TODO: special imports
except ImportError:
    print("Missing dependencies, please run 'sudo pip install ...'")
    sys.exit(1)


# -------------------- CONSTANTS SECTION --------------------
# TODO: define constants here


# -------------------- FUNCTIONS SECTION --------------------
# TODO: define functions here


# --------------------- CLASSES SECTION ---------------------
# TODO: define classes here


# ---------------------- MAIN SECTION -----------------------
"""
IMPORTS = "{item}from tinyscript import *\n"
MAIN = """if __name__ == '__main__':
    parser.add_argument("", help="")
    # TODO: write new arguments
    initialize(globals())
    # TODO: use validate(globals(), ...) if necessary
    # TODO: write logic here{base}
"""

TEMPLATES = ["script", "tool"]
ITEMS = {
    "pybots.HTTPBot": """
    with HTTPBot("...", verbose=True) as bot:
        bot.get()
""",
    "pybots.JSONBot": """
    with JSONBot("...", verbose=True) as bot:
        bot.get()
""",
    "pybots.TCPBot": """
    with TCPBot("...", 1234, verbose=True) as bot:
        bot.send_receive("...")
"""
}


def new(target):
    """
    Function for creating a template script or tool.
    
    :param target: type of script/tool to be created
    """
    assert len(target) <= 2, \
           "Too many arguments"
    template = target[0]
    assert template in TEMPLATES, \
           "First target argument must be one of the followings: {}" \
           .format(TEMPLATES)
    item = target[1] if len(target) == 2 else None
    items = ITEMS.keys()
    assert item is None or item in items, \
           "Second target argument must be one of the followings: {}" \
           .format(items)
    with open("{}.py".format(template), 'w') as f:
        item_import = "" if item is None else "from {} import {}\n" \
                                              .format(*item.split('.'))
        base = ITEMS.get(item)
        main = MAIN.format(base=base or "")
        if template == "script":
            f.write(SHEBANG + IMPORTS.format(item=item_import) + "\n\n" + main)
        elif template == "tool":
            f.write(SHEBANG + TOOL_METADATA + TOOL_SECTIONS \
                    .format(imports=IMPORTS.format(item=item_import)) + main)
