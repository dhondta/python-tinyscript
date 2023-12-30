# -*- coding: UTF-8 -*-
"""Utility functions for retrieving a parser and subparsers from a tool.

"""
from shutil import which

from .path import Path, PythonPath, TempPath
from ..argreparse import ArgumentParser, ProxyArgumentParser


__all__ = __features__ = ["get_parser", "get_parsers"]


def get_parser(tool, logger=None, **kwargs):
    return [p for p in get_parsers(tool, logger=logger, **kwargs).values() if isinstance(p, ArgumentParser) and \
                                                                              not hasattr(p, "_parent")][0]


def get_parsers(tool, logger=None, **kwargs):
    tmp = TempPath(length=16)
    if isinstance(tool, str):
        tool = Path(which(tool), expand=True)
    # copy the target tool to modify it so that its parser tree can be retrieved
    ntool = tool.copy(tmp.joinpath(f"_{tool.basename}.py"))
    ntool.write_text(ntool.read_text().replace("if __name__ == '__main__':", f"{kwargs.pop('cond', '')}\ndef main():") \
                                      .replace("if __name__ == \"__main__\":", "def main():") \
                                      .replace("initialize(", "return parser\n    initialize(") \
                                      .rstrip("\n") + "\n\nif __name__ == '__main__':\n    main()\n")
    ntool.chmod(0o755)
    # populate the real parser and add information arguments
    try:
        __parsers = {PythonPath(ntool).module.main(): ArgumentParser(**kwargs)}
    except Exception as e:
        if logger:
            logger.critical(f"Parser retrieval failed for tool: {tool.basename}")
            logger.error(f"Source ({ntool}):\n{ntool.read_text()}")
            logger.exception(e)
        from sys import exit
        exit(1)
    # now import the populated list of parser calls from within the tinyscript.parser module
    from tinyscript.argreparse import parser_calls
    global parser_calls
    #  proxy parser to real parser recursive conversion function
    def __proxy_to_real_parser(value):
        """ Source: tinyscript.parser """
        if isinstance(value, ProxyArgumentParser):
            return __parsers[value]
        elif isinstance(value, (list, tuple)):
            return [__proxy_to_real_parser(_) for _ in value]
        return value
    #  now iterate over the registered calls
    pairs = []
    for proxy_parser, method, args, kwargs, proxy_subparser in parser_calls:
        kw_category = kwargs.get('category')
        real_parser = __parsers[proxy_parser]
        args = (__proxy_to_real_parser(v) for v in args)
        kwargs = {k: __proxy_to_real_parser(v) for k, v in kwargs.items()}
        # NB: when initializing a subparser, 'category' kwarg gets popped
        real_subparser = getattr(real_parser, method)(*args, **kwargs)
        if real_subparser is not None:
            __parsers[proxy_subparser] = real_subparser
        if not isinstance(real_subparser, str):
            real_subparser._parent = real_parser
            real_subparser.category = kw_category  # reattach category
    tmp.remove()
    ArgumentParser.reset()
    return __parsers

