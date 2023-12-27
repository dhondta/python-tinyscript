# -*- coding: UTF-8 -*-
"""Root module's __conf__.py tests.

"""
from tinyscript.helpers import get_parser, Path
from tinyscript.template import new, TARGETS, TEMPLATE

from utils import *


class TestConf(TestCase):
    def test_parser_retrieval(self):
        script = TEMPLATE.format(base="", target="").replace("# TODO: add arguments", "parser.add_argument('test')")
        with open(".test-script.py", 'wt') as f:
            f.write(script)
        p = get_parser(Path(".test-script.py"))
        subparsers = p.add_subparsers(dest="command")
        test = subparsers.add_parser("subtest", aliases=["test2"], help="test", parents=[p])
        test.add_argument("--test")
        self.assertTrue(hasattr(p, "tokens"))

