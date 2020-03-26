#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Text utility functions' tests.

"""
from tinyscript.helpers.text import *
from tinyscript.helpers.text import configure_docformat, txt_terminal_render, \
                                    _txt_list, _txt_style

from utils import *


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
            self.assertNotEqual(TXT, txt2bold(TXT))

    def test_text_conversions(self):
        txt = TXT.title()
        self.assertEqual(txt2blockquote(TXT, None), TXT)
        self.assertEqual(txt2bold(TXT, None), TXT)
        self.assertEqual(txt2italic(TXT, None), TXT)
        self.assertEqual(txt2olist(TXT, None), TXT)
        self.assertEqual(txt2paragraph(TXT, None), TXT)
        self.assertEqual(txt2title(TXT, None), TXT)
        self.assertEqual(txt2ulist(TXT, None), TXT)
        self.assertEqual(txt2underline(TXT, None), TXT)
        # html format
        self.assertEqual(txt2blockquote(TXT, "html"), 
                         "<blockquote>{}</blockquote>".format(TXT))
        self.assertEqual(txt2bold(TXT, "html"), "<b>{}</b>".format(TXT))
        self.assertEqual(txt2email(EML, "html"), "<a href=\"mailto:{0}\">{0}"
                                                 "</a>".format(EML))
        self.assertEqual(txt2italic(TXT, "html"), "<i>{}</i>".format(TXT))
        self.assertEqual(txt2paragraph(TXT, "html"), "<p>{}</p>".format(TXT))
        self.assertEqual(txt2title(TXT, "html"), "<h2>{}</h2>".format(txt))
        self.assertEqual(txt2ulist(TXT, "html"), "<ul>\n<li>{}</li>\n</ul>"
                                                 .format(TXT))
        self.assertEqual(txt2underline(TXT, "html"), "<u>{}</u>".format(TXT))
        self.assertEqual(txt2url(URL, "html"), "<a href=\"{0}\">{0}</a>"
                                               .format(URL))
        # markdown format
        self.assertEqual(txt2blockquote(TXT, "md"), "> " + TXT)
        self.assertEqual(txt2bold(TXT, "md"), "**{}**".format(TXT))
        self.assertEqual(txt2email(EML, "md"), "[{0}](mailto:{0})".format(EML))
        self.assertEqual(txt2italic(TXT, "md"), "_{}_".format(TXT))
        self.assertEqual(txt2paragraph(TXT, "md"), TXT)
        self.assertEqual(txt2title(TXT, "md"), "## " + txt)
        self.assertEqual(txt2underline(TXT, "md"), "[" + TXT + "]()")
        self.assertEqual(txt2url(URL, "md"), "[{0}]({0})".format(URL))
        # restructuredtext format
        self.assertEqual(txt2blockquote(TXT, "rst"), "\t" + TXT)
        self.assertEqual(txt2bold(TXT, "rst"), "*{}*".format(TXT))
        self.assertEqual(txt2italic(TXT, "rst"), "_{}_".format(TXT))
        self.assertEqual(txt2title(TXT, "rst"), txt + "\n" + "-" * len(TXT))
        self.assertEqual(txt2ulist(TXT, "rst"), "- " + TXT)
        # textile format
        self.assertEqual(txt2blockquote(TXT, "textile"), "\t" + TXT)
        self.assertEqual(txt2email(EML, "textile"), "\"{0}\":mailto:{0}"
                                                     .format(EML))
        self.assertEqual(txt2olist(TXT, "textile"), "# " + TXT)
        self.assertEqual(txt2title(TXT, "textile"), "h2. {} 2".format(txt))
        self.assertEqual(txt2ulist(TXT, "textile"), "* " + TXT)
        self.assertEqual(txt2url(URL, "textile"), "\"$\":{}".format(URL))
        # input validation
        self.assertRaises(ValueError, _txt_list, TXT, format="does_not_exit")
        self.assertRaises(ValueError, _txt_list, TXT, "md", ordered="not_bool")
        self.assertRaises(ValueError, txt2title, TXT, "rst", level="not_int")
        self.assertRaises(ValueError, txt2url, TXT, "md", url="bad_url")
    
    def test_text_rendering(self):
        configure_docformat({'__docformat__': "html"})
        t = txt_terminal_render(txt2title(TXT))
        self.assertIsNotNone(t)
        configure_docformat({'__docformat__': "md"})
        self.assertEqual(txt_terminal_render(txt2title(TXT)), t)
        configure_docformat({'__docformat__': None})
        self.assertEqual(txt_terminal_render(TXT), TXT)
        self.assertRaises(ValueError, txt2email, TXT)
        self.assertRaises(ValueError, txt2url, TXT)
