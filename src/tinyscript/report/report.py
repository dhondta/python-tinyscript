# -*- coding: UTF-8 -*-
"""Module for defining Report.

"""
import logging
from os import listdir
from os.path import abspath, dirname, isfile, join, splitext
try:
    from weasyprint import CSS, HTML
    pdf_generation = True
except ImportError:
    pdf_generation = False

from .base import *
from .objects import *
from ..helpers import ensure_str
from ..preimports import logging


__all__ = __features__ = ["Report"]

PAGE_CSS = "@page{size:%(size)s;margin:%(margins)s;%(header)s%(footer)s}"


class Report(list):
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
        self.title = options.get('title')
        self.clear()
        self.append(*pieces)
    
    def __handle(self, piece):
        p = piece
        if p.__class__.__name__ == "Footer":
            if self.footer:
                return
            self.footer = p.css
        elif p.__class__.__name__ == "Header":
            if self.header:
                return
            self.header = p.css
        elif not isinstance(p, Element):
            p = Text(str(p))
        c = p.__class__.__name__.lower()
        self.__counts.setdefault(c, 0)
        self.__counts[c] += 1
        p.id = self.__counts[c]
        if self.__counts[c] > 1:
            if self.__counts[c] == 2:
                for p2 in self:
                    if p2.__class__.__name__.lower() == p2.name == c:
                        p2.name += "-%d" % p2.id
            if p.name == c:
                p.name += "-%d" % p.id
        return p
    
    def append(self, *pieces):
        for p in pieces:
            p = self.__handle(p)
            if p:
                super(Report, self).append(p)
    
    def clear(self):
        self.__counts = {}
        self.header = ""
        self.footer = ""
        if self.title:
            self.insert(0, Title(self.title))
    
    def copy(self):
        r = Report(**self.__dict__)
        r.append(*self)
        return r
    
    def count(self, piece_class):
        return self.__counts[piece_class.lower()]
    
    def extend(self, pieces):
        self.append(*pieces)
    
    def index(self, name):
        for p in self:
            if p.name == name:
                return p
        raise ValueError("'{}' is not in list".format(name))
    
    def insert(self, index, piece):
        p = self.__handle(piece)
        if p:
            super(Report, self).insert(index, p)
    
    def prepend(self, *pieces):
        for p in pieces[::-1]:
            p = self.__handle(p)
            if p:
                super(Report, self).insert(0, p)
    
    @property
    def counts(self):
        return self.__counts
    
    @property
    def themes(self):
        return list(map(lambda f: splitext(f)[0], filter(lambda f: f.endswith(".css"), listdir(dirname(__file__)))))
    
    @output
    def csv(self, text=TEXT):
        return "\n\n".join(p.csv(text=True) for p in self if p.csv(text=True) != "")
    
    @output
    def html(self, indent=4, text=TEXT):
        """ Generate an HTML file from the report data. """
        ind = (indent or 0) * " "
        self.logger.debug("Generating the HTML report{}...".format(["", " (text only)"][text]))
        r = []
        for p in self:
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
        for p in self:
            if isinstance(p, (Data, List, Table)) or not data_only:
                r.update(p.json(text=True))
        return r
    
    @output
    def md(self, text=TEXT):
        r = []
        for p in self:
            if p.md().strip() != "":
                r.append(p.md())
        return "\n\n".join(r)
    
    @output
    def rst(self, text=TEXT):
        r = []
        for p in self:
            if p.rst().strip() != "":
                r.append(p.rst())
        return "\n\n".join(r)

    @output
    def pdf(self, text=TEXT):
        """ Generate a PDF file from the report data. """
        if pdf_generation:
            self.logger.debug("Generating the PDF report...")
            html = HTML(string=self.html())
            fn = self.filename if self.filename.endswith(".pdf") else "%s.pdf" % self.filename
            html.write_pdf(fn, stylesheets=[self.css, CSS(string=PAGE_CSS % self.__dict__)])
    
    @output
    def xml(self, indent=2, data_only=False, text=TEXT):
        r = ["<report>"]
        for p in self:
            if isinstance(p, (Data, List, Table)) or not data_only:
                out = ensure_str(p.xml(indent=indent, text=True))
                for line in out.split("\n"):
                    r.append((indent or 0) * " " + line)
        r.append("</report>")
        r = ("" if indent is None else "\n").join(r)
        return r

