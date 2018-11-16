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
from os.path import exists, splitext
from six import string_types
from weasyprint import CSS, HTML

from .__info__ import __author__, __copyright__, __version__


__all__ = __features__ = ["Footer", "Header", "Report", "Section", "Table",
                          "Text", "Title"]

HEAD_CSS = "@%(pos)s-left{%(left)s};@%(pos)s-center{%(center)s};@%(pos)s-righ" \
           "t{%(right)s};"
PAGE_CSS = "@page{size:%(size)s;margin:%(margins)s;%(header)s%(footer)s}"
PDF_CSS = "h1,h3{line-height:1}address,blockquote,dfn,em{font-style:italic}ht" \
          "ml{font-size:100.01%}body{font-size:75%;color:#222;background:#fff" \
          ";font-family:\"Helvetica Neue\",Arial,Helvetica,sans-serif}h1,h2,h" \
          "3,h4,h5,h6{font-weight:400;color:#111}h1{font-size:3em;margin-bott" \
          "om:.5em}h2{font-size:2em;margin-bottom:.75em}h3{font-size:1.5em;ma" \
          "rgin-bottom:1em}h4{font-size:1.2em;line-height:1.25;margin-bottom:" \
          "1.25em}h5,h6{font-size:1em;font-weight:700}h5{margin-bottom:1.5em}" \
          "h1 img,h2 img,h3 img,h4 img,h5 img,h6 img{margin:0}p{margin:0 0 1." \
          "5em}.left{float:left!important}p .left{margin:1.5em 1.5em 1.5em 0;" \
          "padding:0}.right{float:right!important}p .right{margin:1.5em 0 1.5" \
          "em 1.5em;padding:0}address,dl{margin:0 0 1.5em}a:focus,a:hover{col" \
          "or:#09f}a{color:#06c;text-decoration:underline}.quiet,blockquote,d" \
          "el{color:#666}blockquote{margin:1.5em}dfn,dl dt,strong,th{font-wei" \
          "ght:700}sub,sup{line-height:0}abbr,acronym{border-bottom:1px dotte" \
          "d #666}pre{margin:1.5em 0;white-space:pre}code,pre,tt{font:1em 'an" \
          "dale mono','lucida console',monospace;line-height:1.5}li ol,li ul{" \
          "margin:0}ol,ul{margin:0 1.5em 1.5em 0;padding-left:1.5em}ul{list-s" \
          "tyle-type:disc}ol{list-style-type:decimal}dd{margin-left:1.5em}tab" \
          "le{margin-bottom:1.4em;width:100%}thead th{background:#c3d9ff}capt" \
          "ion,td,th{padding:4px 10px 4px 5px}tbody tr.even td,tbody tr:nth-c" \
          "hild(even) td{background:#e5ecf9}tfoot{font-style:italic}caption{b" \
          "ackground:#eee}.small{font-size:.8em;margin-bottom:1.875em;line-he" \
          "ight:1.875em}.large{font-size:1.2em;line-height:2.5em;margin-botto" \
          "m:1.25em}.hide{display:none}.loud{color:#000}.highlight{background" \
          ":#ff0}.added{background:#060;color:#fff}.removed{background:#900;c" \
          "olor:#fff}.first{margin-left:0;padding-left:0}.last{margin-right:0" \
          ";padding-right:0}.top{margin-top:0;padding-top:0}.bottom{margin-bo" \
          "ttom:0;padding-bottom:0}"
TEXT = True


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
            if exists(filename):
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
        self.filename = options.get('filename', "report") or "report"
        self.logger = options.get('logger', logging.getLogger("main"))
        self.size = options.get('size', "a4 portrait")
        self.margins = options.get('margins', "10.0mm 20.0mm 20.0mm 20.0mm")
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
        css = [CSS(string=PDF_CSS), CSS(string=PAGE_CSS % self.__dict__)]
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
