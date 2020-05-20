# -*- coding: UTF-8 -*-
"""Module for defining Report.

"""
import logging
from os import listdir
from os.path import abspath, dirname, isfile, join, splitext
from weasyprint import CSS, HTML

from .base import *
from .objects import *
from ..helpers import ensure_str
from ..preimports import logging


__all__ = __features__ = ["Report"]

PAGE_CSS = "@page{size:%(size)s;margin:%(margins)s;%(header)s%(footer)s}"


class Report(object):
    """ This class represents a whole report. """
    page_css = "@page{size:%(size)s;margin:%(margins)s;%(header)s%(footer)s}"
    
    @logging.bindLogger
    def __init__(self, *pieces, **options):
        self.filename = options.get('filename', "report") or "report"
        self.size = options.get('size', "a4 portrait")
        self.margins = options.get('margins', "10.0mm 20.0mm 20.0mm 20.0mm")
        self.theme = options.get('theme', "default")
        if self.theme not in self.themes:
            raise ValueError("PDF report CSS theme does not exist")
        self.css = options.get('css', join(dirname(abspath(__file__)), "{}.css".format(self.theme)))
        self.css = abspath(self.css)
        if not isfile(self.css):
            raise ValueError("PDF report CSS file does not exist")
        self._pieces = []
        self.header = ""
        self.footer = ""
        title = options.get('title')
        if title:
            pieces = list(pieces)
            pieces.insert(0, Title(title))
        counts = {}
        has_footer, has_header = False, False
        for p in pieces:
            if isinstance(p, Footer) and has_footer or isinstance(p, Header) and has_header:
                continue
            if not isinstance(p, Element):
                p = Text(str(p))
            c = p.__class__.__name__.lower()
            counts.setdefault(c, 0)
            counts[c] += 1
            p.id = counts[c]
            self._pieces.append(p)
            if isinstance(p, Footer):
                has_footer = True
                self.footer = p.css
            if isinstance(p, Header):
                has_header = True
                self.header = p.css
        for p in self._pieces:
            c = p.__class__.__name__.lower()
            if p.name.endswith("-0"):
                p.name = "%s-%d" % (c, p.id) if counts[c] > 1 else c
    
    @property
    def themes(self):
        return list(map(lambda f: splitext(f)[0], filter(lambda f: f.endswith(".css"), listdir(dirname(__file__)))))
    
    @output
    def csv(self, text=TEXT):
        return "\n\n".join(p.csv(True) for p in self._pieces if p.csv(True) != "")
    
    @output
    def html(self, indent=4, text=TEXT):
        """ Generate an HTML file from the report data. """
        ind = (indent or 0) * " "
        self.logger.debug("Generating the HTML report{}...".format(["", " (text only)"][text]))
        r = []
        for p in self._pieces:
            h = p.html(indent=indent, text=True)
            if h != "":
                r.append(h)
        nl = "" if indent is None else "\n"
        h = (nl + "<br>" + nl).join(r).replace("\\\"", "\"")
        r = []
        for line in h.split("\n"):
            r.append(2 * ind + line)
        r = ["<html>", ind + "<body>"] + r + [ind + "</body>", "</html>"]
        return nl.join(r)
    
    @output
    def json(self, data_only=False, text=TEXT):
        r = {}
        for p in self._pieces:
            if isinstance(p, (Data, List, Table)) or not data_only:
                r.update(p.json(True))
        return r
    
    @output
    def md(self, text=TEXT):
        r = []
        for p in self._pieces:
            if p.md() != "":
                r.append(p.md())
        return "\n\n".join(r)

    @output
    def pdf(self, text=TEXT):
        """ Generate a PDF file from the report data. """
        self.logger.debug("Generating the PDF report...")
        html = HTML(string=self.html())
        html.write_pdf("%s.pdf" % self.filename, stylesheets=[self.css, CSS(string=PAGE_CSS % self.__dict__)])
    
    @output
    def xml(self, indent=2, data_only=False, text=TEXT):
        r = ["<report>"]
        for p in self._pieces:
            if isinstance(p, (Data, List, Table)) or not data_only:
                out = ensure_str(p.xml(indent=indent, text=True))
                for line in out.split("\n"):
                    r.append((indent or 0) * " " + line)
        r.append("</report>")
        r = ("" if indent is None else "\n").join(r)
        return r

