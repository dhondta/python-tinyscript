#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for making a report from markdown/HTML to PDF or other individual
 elements to various formats.

"""
import json
import logging
import markdown2
import numpy as np
import pandas as pd
from os import listdir
from os.path import abspath, dirname, exists, isfile, join, splitext
from six import string_types
from weasyprint import CSS, HTML

from ..__info__ import __author__, __copyright__, __version__


__features__ = ["Footer", "Header", "Section", "Table", "Text", "Title"]
__all__ = ["Report"] + __features__

HEAD_CSS = "@%(pos)s-left{%(left)s};@%(pos)s-center{%(center)s};@%(pos)s-righ" \
           "t{%(right)s};"
PAGE_CSS = "@page{size:%(size)s;margin:%(margins)s;%(header)s%(footer)s}"
TEXT = True
THEMES = list(map(lambda f: splitext(f)[0],
                  filter(lambda f: f.endswith(".css"),
                              listdir(dirname(__file__)))))


def output(f):
    """ This decorator allows to choose to return an output as text or to save
         it to a file. """
    def wrapper(self, *args, **kwargs):
        try:
            text = kwargs.get('text') or args[0]
        except IndexError:
            text = True
        _ = f(self, *args, **kwargs)
        if text:
            return _
        elif _ is not None and isinstance(_, string_types):
            filename = "{}.{}".format(self.filename, f.__name__)
            while exists(filename):
                name, ext = splitext(filename)
                try:
                    name, i = name.split('-')
                    i = int(i) + 1
                except ValueError:
                    i = 2
                filename = "{}-{}".format(name, i) + ext
            with open(filename, 'w') as out:
                out.write(_)
    return wrapper


class Element(object):
    """ This class is used to give a common type to report elements. """
    pass


class Footer(Element):
    """ This class represents the footer of a report. """
    pos = "bottom"
    
    def __init__(self, left="", center="", right=""):
        self.pos = self.__class__.pos
        if self.pos == "bottom" and center == "":
            center = "\" counter(page) \"/\" counter(pages) \""
        for elm in ["left", "center", "right"]:
            val = locals()[elm]
            if isinstance(val, string_types):
                val = Text(val, size=9)
            if isinstance(val, Text):
                setattr(self, elm, val.css())

    @output
    def css(self, text=TEXT):
        return HEAD_CSS % self.__dict__


class Header(Footer):
    """ This class represents the header of a report. """
    pos = "top"


class Report(object):
    """ This class represents a whole report. """
    page_css = "@page{size:%(size)s;margin:%(margins)s;%(header)s%(footer)s}"
    
    def __init__(self, *pieces, **options):
        self.css = options.get('css')
        self.filename = options.get('filename', "report") or "report"
        self.logger = options.get('logger', logging.getLogger("main"))
        self.margins = options.get('margins', "10.0mm 20.0mm 20.0mm 20.0mm")
        self.size = options.get('size', "a4 portrait")
        self.theme = options.get('theme', "default")
        if self.theme not in THEMES:
            raise ValueError("PDF report CSS theme does not exist")
        if self.css:
            if not isfile(self.css):
                self.css = None
            else:
                self.css = abspath(self.css)
        self.header = ""
        self.footer = ""
        title = options.get('title') or ""
        self._pieces = []
        if title != "":
            self._pieces.append(Title(title))
        for piece in pieces:
            if isinstance(piece, Header):
                self.header = piece.css()
            elif isinstance(piece, Footer):
                self.footer = piece.css()
            else:
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
                html.append(markdown2.markdown(piece, extras=["tables"]))
            elif isinstance(piece, Element):
                html.append(piece.html())
        return "\n\n".join(html)
    
    @output
    def json(self, text=TEXT):
        return self._table_output("json", text)
    
    @output
    def md(self, text=TEXT):
        pieces = []
        for piece in self._pieces:
            if isinstance(piece, string_types):
                pieces.append(piece)
            else:
                try:
                    pieces.append(piece.md())
                except:
                    pass
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


class Table(Element):
    """ This class represents a table. """
    filename = "table"
    
    def __init__(self, data, col_headers=None, row_headers=None):
        array = np.array(data) if not isinstance(data, np.ndarray) else data
        kw = {}
        if col_headers is not None:
            kw['columns'] = col_headers
        if row_headers is not None:
            kw['index'] = row_headers
        self._data = pd.DataFrame(data, **kw)
    
    @output
    def csv(self, text=TEXT, sep=',', index=True, float_fmt="%.2g"):
        """ Generate a CSV table from the table data. """
        return self._data.to_csv(sep=sep, index=index, float_format=float_fmt)
    
    @output
    def html(self, text=TEXT):
        """ Generate an HTML table from the table data. """
        return self._data.to_html()
    
    @output
    def json(self, text=TEXT):
        """ Generate a JSON object form the table data. """
        return self._data.to_json(orient='index')
    
    @output
    def md(self, text=TEXT, float_format="%.2g"):
        """ Generate Markdown from the table data. """
        cols = self._data.columns
        hl = pd.DataFrame([["---"] * len(cols)], index=["---"], columns=cols)
        df = pd.concat([hl, self._data])
        return df.to_csv(sep='|', index=True, float_format=float_format)
    
    @output
    def xml(self, text=TEXT):
        """ Generate an XML output from the report data. """
        def convert(line):
            xml = "  <item>\n"
            for f in line.index:
                xml += "    <field name=\"%s\">%s</field>\n" % (f, line[f])
            xml += "  </item>\n"
            return xml
        return "<items>\n" + '\n'.join(self._data.apply(convert, axis=1)) + \
               "</items>"


class Text(Element):
    def __init__(self, content, size="12", style="normal", color="black",
                 tag="p"):
        self.content = content
        self.tag = tag
        self.style = "font-size:%(size)spx;font-style:%(style)s;color:" \
                     "%(color)s;" % locals()
    
    @output
    def css(self, text=TEXT):
        return "content:\"%(content)s\";%(style)s" % self.__dict__
    
    @output
    def html(self, text=TEXT):
        return "<%(tag)s style=\"%(style)s\">%(content)s</%(tag)s>" % \
               self.__dict__
    
    @output
    def md(self, text=TEXT):
        return self.content


class Title(Text):
    def __init__(self, title, style="normal", color="black", tag="h1"):
        self.content = title
        self.tag = tag
        self.style = "font-style:%(style)s;color:%(color)s;" % locals()
    
    @output
    def md(self, text=TEXT):
        i = int(self.tag[-1])
        return "%(prefix)s %(content)s" % {'prefix': "#" * i,
                                           'content': self.content}


class Section(Title):
    def __init__(self, title, style="normal", color="black", tag="h2"):
        super(Section, self).__init__(title, style, color, tag)
