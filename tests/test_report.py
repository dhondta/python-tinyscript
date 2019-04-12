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
                self.assertTrue(e("test").css())
            for e in [Text, Title, Section]:
                o = e("test")
                self.assertTrue(o.html())
                self.assertTrue(o.md())
        
        def test_report_table_element(self):
            t = Table([[1, 2]], ["test1", "test2"], ["test3"])
            for fmt in ["csv", "html", "json", "md", "xml"]:
                self.assertTrue(getattr(t, fmt)())
        
        def test_report_text_generation(self):
            r = Report(
                Title("Test"),
                Header("test header"),
                Footer("test footer"),
                Table([[1, 2]]),
                Section("test section"),
                Text("test text"),
                Section("bad section", tag="a"),
                "Free text",
            )
            for fmt in ["csv", "html", "json", "md", "xml"]:
                self.assertTrue(getattr(r, fmt)())
            r.pdf()
            self.assertTrue(exists("report.pdf"))
            remove("report.pdf")
        
        def test_report_file_generation(self):
            r = Report(title="Test")
            r.html(False)
            r.html(False)
            r.html(False)
            remove("report.html")
            remove("report-2.html")
            remove("report-3.html")
        
        def test_report_assets(self):
            self.assertRaises(ValueError, Report, theme="does_not_exist")
            self.assertIs(Report(css="does_not_exist").css, None)
            self.assertTrue(Report(css="tinyscript/report/default.css").css)
