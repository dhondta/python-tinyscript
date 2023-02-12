#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tinyscript import *
from tinyscript.template import new as new_script, TARGETS

from tinyscript.__info__ import __author__, __copyright__, __email__, __license__, __version__


__script__   = "tinyscript"
__examples__ = ["test", "my-script -t pybots.HTTPBot"]
__doc__      = """
This tool allows to quickly create a new Tinyscript script/tool from a template.
"""


def main():
    commands = parser.add_subparsers(dest="command", help="command to be executed")
    new = commands.add_parser("new", help="make a new script")
    new.add_argument("name", type=ts.str_matches(r"^([0-9a-z]+[-_]+)?[0-9a-z]+$", re.I), help="script name")
    new.add_argument("-t", "--target", choices=TARGETS.keys(), help="target to be created")
    install = commands.add_parser("install", help="install a publicly available script")
    search = commands.add_parser("search", help="search for a publicly available script")
    update = commands.add_parser("update", help="update the list of publicly available scripts")
    update.add_argument("-s", "--source", nargs="*", help="set a source URL for a list of scripts")
    initialize(noargs_action="wizard")
    if args.command == "new":
        new_script(args.name, args.target)
    elif args.command == "install":
        # install from a source where the tool can be found
        raise NotImplementedError
    elif args.command == "search":
        # search for a tool
        raise NotImplementedError
    elif args.command == "update":
        with open(ts.ConfigPath("Tinyscript").join("sources.conf")) as f:
            for l in f:
                source = l.strip()
                if source == "" or source.startswith("#"):
                    continue
                # do something with source

