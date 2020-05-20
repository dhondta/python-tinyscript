#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Report module assets' tests.

"""
from utils import *


if PYTHON3:  # report module only available from Python3
    from tinyscript.report import *
    
    
    class TestReport(TestCase):
        def test_report_text_elements(self):
            for e in [Footer, Header, Text, Title, Section]:
                self.assertTrue(e("test").css)
            for e in [Text, Title, Section]:
                o = e("test")
                self.assertTrue(o.html())
                self.assertTrue(o.md())
            self.assertRaises(ValueError, Section, "bad section", tag="a")
        
        def test_report_table_element(self):
            t = Table([[1, 2]], ["test1", "test2"], ["test3"])
            for fmt in ["csv", "html", "json", "md", "xml"]:
                self.assertTrue(getattr(t, fmt)())
        
        def test_report_text_generation(self):
            r = Report(
                Title("Test"),
                Header("test header"),
                Footer("test footer"),
                Header("useless header"),
                Footer("useless footer"),
                List("item1", "itme2"),
                Table([[1, 2]]),
                Section("test section"),
                Subsection("test subsection"),
                Data({'test': "Test string", 'data': {'a': 1, 'b': 2}}),
                Text("test text"),
                Code("#test\nprint('hello')", language="python", hl_lines="1"),
                "Free text",
            )
            for fmt in ["csv", "html", "json", "md", "xml"]:
                self.assertTrue(getattr(r, fmt)())
            r.pdf()
            self.assertTrue(exists("report.pdf"))
            remove("report.pdf")
        
        def test_report_file_generation(self):
            r = Report(title="Test")
            for i in range(3):
                r.html(False)
            remove("report.html")
            remove("report-2.html")
            remove("report-3.html")
        
        def test_report_assets(self):
            self.assertRaises(ValueError, Report, theme="does_not_exist")
            self.assertTrue(Report(css="tinyscript/report/default.css").css)
            self.assertTrue(Report(theme="default").css)
            self.assertRaises(ValueError, Data, "BAD DATA ; SHOULD BE DICT")
