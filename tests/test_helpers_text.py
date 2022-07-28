#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Text utility functions' tests.

"""
from tinyscript.helpers.text import *
from tinyscript.helpers.text import configure_docformat, txt_terminal_render, _txt_list, _txt_style

from utils import *


HTML = """<h1>Tool 1.0</h1>
<p><b>Author</b>: John Doe (<a href="mailto:john.doe@example.com">john.doe@example.com</a>)
<blockquote>Something ...</blockquote>
<h2>Usage</h2>:
<p>./tool.py [--test A_TEST_VAR] [-h] [-v]</p>
<h2>Extra Arguments</h2>:
<p>-h, --help     show this help message and exit</p>
<p>-v, --verbose  verbose mode (default: False)</p>
<h2>Usage Example</h2>:
<p>./tool.py ...</p>"""


MD = """# Tool 1.0

*Author*: John Doe ([john.doe@example.com](mailto:john.doe@example.com))

> Something ...

## Usage:

./tool.py [--test A_TEST_VAR] [-h] [-v]

## Extra Arguments:

-h, --help     show this help message and exit

-v, --verbose  verbose mode (default: False)

## Usage Example:

./tool.py ..."""


RST = """Tool 1.0
========

*Author*: John Doe (john.doe@example.com)

    Something ...

Usage:
------

./tool.py [--test A_TEST_VAR] [-h] [-v]

Extra Arguments:
----------------

-h, --help     show this help message and exit

-v, --verbose  verbose mode (default: False)


Usage Example:
--------------

./tool.py ..."""


TEXTILE = """h1. Tool 1.0

*Author*: John Doe ("john.doe@example.com":mailto:john.doe@example.com)

bq. Something ...

h2. Usage:

./tool.py [--test A_TEST_VAR] [-h] [-v]

h2. Extra Arguments:

-h, --help     show this help message and exit

-v, --verbose  verbose mode (default: False)


h2. Usage Example:

./tool.py ..."""


class TestHelpersText(TestCase):
    def setUp(self):
        global EML, URL, TXT
        EML = "john.doe@example.com"
        URL = "https://john:doe@www.example.com/path?p=true"
        TXT = "test string"
        configure_docformat({'__docformat__': None})
    
    def test_docformat_config(self):
        from tinyscript.helpers.text import FORMATS
        self.assertEqual(TXT, txt2bold(TXT))
        for fmt in FORMATS[1:]:
            configure_docformat({'__docformat__': fmt})
            for f in [txt2bold, txt2italic, txt2underline]:
                [self.assertNotEqual, self.assertEqual][fmt == "console"](TXT, f(TXT, fmt))

    def test_text_conversions(self):
        # input validation
        self.assertRaises(ValueError, _txt_list, TXT, format="does_not_exit")
        self.assertRaises(ValueError, _txt_list, TXT, "md", ordered="not_bool")
        self.assertRaises(ValueError, txt2title, TXT, "rst", level="not_int")
        self.assertRaises(ValueError, txt2url, TXT, "md", url="bad_url")
        # test that conversions do not fail
        txt = TXT.title()
        for f in [txt2blockquote, txt2bold, txt2code, txt2comment, txt2email, txt2italic, txt2olist, txt2paragraph,
                  txt2preformatted, txt2title, txt2ulist, txt2underline, txt2url]:
            inp = EML if f.__name__.endswith("email") else URL if f.__name__.endswith("url") else TXT
            self.assertEqual(f(inp, None), inp)
            for fmt in ["html", "md", "rst", "textile"]:
                self.assertIsNotNone(f(inp, fmt))
    
    def test_text_rendering(self):
        configure_docformat({'__docformat__': "html"})
        t = txt_terminal_render(txt2title(TXT), debug=True)
        self.assertIsNotNone(t)
        configure_docformat({'__docformat__': "md"})
        self.assertEqual(txt_terminal_render(txt2title(TXT)), t)
        configure_docformat({'__docformat__': None})
        self.assertEqual(txt_terminal_render(TXT), TXT)
        self.assertRaises(ValueError, txt2email, TXT)
        self.assertRaises(ValueError, txt2url, TXT)
        for help, fmt in zip([HTML, MD, RST, TEXTILE], ["html", "md", "rst", "textile"]):
            self.assertIsNotNone(txt_terminal_render(help, fmt))
    
    def test_text_utils(self):
        self.assertEqual(list(hexdump(URL)), ["00000000:  6874 7470 733a 2f2f 6a6f 686e 3a64 6f65  https://john:doe",
                                              "00000010:  4077 7777 2e65 7861 6d70 6c65 2e63 6f6d  @www.example.com",
                                              "00000020:  2f70 6174 683f 703d 7472 7565            /path?p=true"])
        self.assertEqual(list(hexdump(URL, width=4, first=1)), ["00000000:  6874 7470  http"])
        self.assertEqual(list(hexdump(URL, width=4, last=1)), ["00000028:  7472 7565  true"])
        self.assertEqual(slugify("This is a test"), "this-is-a-test")
        self.assertEqual(ansi_seq_strip("\x1b[93;41mtest\x1b[0m"), "test")
        self.assertEqual(ansi_seq_strip(b"\x1b[93;41mtest\x1b[0m"), b"test")

