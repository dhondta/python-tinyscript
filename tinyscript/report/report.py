# -*- coding: UTF-8 -*-
"""Module for defining Report.

"""
import logging
from markdown2 import markdown
from os import listdir
from os.path import abspath, dirname, isfile, join, splitext
from weasyprint import CSS, HTML

from .base import *
from .objects import *


__all__ = __features__ = ["Report"]

PAGE_CSS = "@page{size:%(size)s;margin:%(margins)s;%(header)s%(footer)s}"
THEMES = list(map(lambda f: splitext(f)[0],
                  filter(lambda f: f.endswith(".css"),
                              listdir(dirname(__file__)))))


class Report(object):
    """ This class represents a whole report. """
    page_css = "@page{size:%(size)s;margin:%(margins)s;%(header)s%(footer)s}"
    
    def __init__(self, *pieces, **options):
        self.css = options.get('css')
        self.filename = options.get('filename', "report") or "report"
        self.logger = options.get('logger', logging.getLogger("main"))
        self.margins = options.get('margins', "10.0mm 20.0mm 20.0mm 20.0mm")
        self.noerror = options.get('noerror', True)
        self.size = options.get('size', "a4 portrait")
        self.theme = options.get('theme', "default")
        if self.theme not in THEMES:
            raise ValueError("PDF report CSS theme does not exist")
        if self.css:
            if not isfile(self.css):
                self.css = None
            else:
                self.css = abspath(self.css)
        self._pieces = []
        self.header = ""
        self.footer = ""
        title = options.get('title')
        if title:
            self._pieces.append(Title(title))
        for piece in pieces:
            self._pieces.append(piece)
    
    def _table_output(self, fmt, text=TEXT):
        results = []
        for piece in self._pieces:
            if not isinstance(piece, Table):
                continue
            results.append(getattr(piece, fmt)(text))
        return results
    
    @output
    def csv(self, text=TEXT):
        return self._table_output("csv", text)

    @output
    def html(self, text=TEXT):
        """ Generate an HTML file from the report data. """
        self.logger.debug("Generating the HTML report{}..."
                          .format(["", " (text only)"][text]))
        html = []
        for piece in self._pieces:
            if isinstance(piece, string_types):
                html.append(markdown(piece, extras=["tables"]))
            elif isinstance(piece, Element) and hasattr(piece, "html"):
                html.append(piece.html())
        return "\n<br>\n".join(html).replace("\\\"", "\"")
    
    @output
    def json(self, text=TEXT):
        return self._table_output("json", text)
    
    @output
    def md(self, text=TEXT):
        pieces = []
        for piece in self._pieces:
            if isinstance(piece, string_types):
                pieces.append(piece)
            elif isinstance(piece, Element) and hasattr(piece, "md"):
                try:
                    pieces.append(piece.md())
                except ValueError as e:
                    if not self.noerror:
                        raise e
        return "\n\n".join(pieces)

    @output
    def pdf(self, text=TEXT):
        """ Generate a PDF file from the report data. """
        self.logger.debug("Generating the PDF report...")
        html = HTML(string=self.html())
        css_file = self.css or join(dirname(abspath(__file__)),
                                    "{}.css".format(self.theme))
        css = [css_file, CSS(string=PAGE_CSS % self.__dict__)]
        html.write_pdf("{}.pdf".format(self.filename), stylesheets=css)
    
    @output
    def xml(self, text=TEXT):
        return self._table_output("xml", text)
