#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Report module assets' tests.

"""
from tinyscript.report import *

from utils import *


class TestReport(TestCase):
    def __try_formats(self, element):
        for fmt in ["csv", "html", "json", "md", "rst", "xml"]:
            self.assertIsNotNone(getattr(element, fmt)())
    
    def test_report_text_elements(self):
        for e in [Blockquote, Code, Text, Title, Section, Subsection]:
            o = e("test")
            self.__try_formats(o)
        self.assertRaises(ValueError, Section, "bad section", tag="a")
        self.assertIsNotNone(List("a", "b"))
        self.assertIsNotNone(List(["a", "b"]))
    
    def test_report_methods(self):
        r = Report(title="Test")
        e = Header("test header")
        self.__try_formats(e)
        r.prepend(e)
        e = Footer("test footer")
        self.__try_formats(e)
        r.append(e)
        r.insert(0, Header("useless header"))
        r.insert(r.index("header"), Footer("useless footer"))
        self.assertTrue(r.count("footer"))
        l = []
        for e in [List("item1", Text("item2"), color="grey"),
                  Table([[1, 2]], ["test1", "test2"], ["test3"]),
                  Section("test section", useless=None),
                  Subsection("test subsection", does_not_throw="error"),
                  Data({'test': "Test string", 'data': {'a': 1, 'b': 2}}),
                  Text("test text", size="10"),
                  Image("test_image.png", width="50%"),
                  Blockquote("test blockquote", size=11),
                  Rule(),
                  Code("#test\nprint('hello')", language="python", hl_lines="1", line_numbers=True)]:
            self.__try_formats(e)
            l.append(e)
        r.extend(l)
        r.append("Free text")
        self.__try_formats(r)
        r.pdf()
        if PYTHON3:
            self.assertTrue(exists("report.pdf"))
            remove("report.pdf")
        r.clear()
        r2 = r.copy()
        self.assertNotEqual(id(r), id(r2))
        self.assertRaises(ValueError, r.index, "does_not_exist")
        self.assertTrue(r.counts)
    
    def test_report_file_generation(self):
        r = Report(title="Test")
        self.assertIsNotNone(repr(r))
        for i in range(3):
            r.html(False)
        remove("report.html")
        remove("report-2.html")
        remove("report-3.html")
    
    def test_report_assets(self):
        self.assertRaises(ValueError, Report, css="does_not_exist")
        self.assertRaises(ValueError, Report, theme="does_not_exist")
        self.assertTrue(Report(css="src/tinyscript/report/default.css").css)
        self.assertTrue(Report(theme="default").css)
        self.assertRaises(ValueError, Data, "BAD DATA ; SHOULD BE DICT")
        self.assertRaises(ValueError, Table, [["a"]], column_headers=["1", "2"])
        self.assertRaises(ValueError, Table, [["a"]], row_headers=["1", "2"])
        self.__try_formats(Table([["a", "b"]], column_footers=["1", "2"]))
        self.__try_formats(Table([["a", "b"]], column_headers=None))
        self.__try_formats(Table([["a", "b"]], row_headers="indices"))
        self.__try_formats(Table([[1, 2]], ["test1", "test2"], ["test3"]))

