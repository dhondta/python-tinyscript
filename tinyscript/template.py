#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import re


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
IMPORTS = "{target}from tinyscript import *\n"
MAIN = """if __name__ == '__main__':
    parser.add_argument("", help="")
    # TODO: write new arguments
    initialize(globals())
    # TODO: use validate(globals(), ...) if necessary
    # TODO: write logic here{base}
"""

TEMPLATES = ["script", "tool"]
TARGETS = {
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

NAME_REGEX = re.compile(r'^([0-9a-z]+[-_]+)?[0-9a-z]+$', re.I)


def new(template, target=None, name=None):
    """
    Function for creating a template script or tool.
    
    :param template: template to be used ; one of TEMPLATES
    :param target:   type of script/tool to be created
    :param name:     name of the new script/tool
    """
    if template not in TEMPLATES:
        raise ValueError("Template argument must be one of the followings: {}"
                         .format(", ".join(TEMPLATES)))
    if target is not None and target not in TARGETS.keys():
        raise ValueError("Target argument must be one of the followings: {}"
                         .format(TARGETS.keys()))
    name = name or template
    if NAME_REGEX.match(name) is None:
        raise ValueError("Invalid {} name".format(template))
    with open("{}.py".format(name), 'w') as f:
        target_imp = "" if target is None else "from {} import {}\n" \
                                               .format(*target.split('.'))
        main = MAIN.format(base=TARGETS.get(target) or "")
        if template == "script":
            f.write(SHEBANG + IMPORTS.format(target=target_imp) + "\n\n" + main)
        elif template == "tool":
            f.write(SHEBANG + TOOL_METADATA + TOOL_SECTIONS \
                    .format(imports=IMPORTS.format(target=target_imp)) + main)
