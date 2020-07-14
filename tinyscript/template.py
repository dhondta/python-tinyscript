#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import re


__all__ = ["new"]


TARGETS = {
    'pybots.HTTPBot': """
    with HTTPBot("...", verbose=True) as bot:
        bot.get()
""",
    'pybots.JSONBot': """
    with JSONBot("...", verbose=True) as bot:
        bot.get()
""",
    'pybots.TCPBot': """
    with TCPBot("...", 1234, verbose=True) as bot:
        bot.send_receive("...")
"""
}
TEMPLATE = """#!/usr/bin/env python
# -*- coding: UTF-8 -*-
{target}from tinyscript import *
# TODO: fill in imports


__author__ = "Your name"
__email__ = "your.name@example.com"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
#__reference__ = ""
#__source__ = ""
#__training__ = ""
# TODO: fill in the docstring
__doc__ = \"\"\"
This tool ...
\"\"\"
# TODO: fill in examples
__examples__ = [""]


if __name__ == '__main__':
    # TODO: add arguments
    initialize()
    # TODO: write logic here{base}
"""


def new(name, target=None):
    """
    Function for creating a template script.
    
    :param name:     name of the new script/tool
    :param target:   type of script to be created, a value among TARGETS' keys
    """
    with open("{}.py".format(name), 'w') as f:
        target_imp = "" if target is None else "from {} import {}\n".format(*target.split('.'))
        f.write(TEMPLATE.format(base=TARGETS.get(target) or "", target=target_imp))

