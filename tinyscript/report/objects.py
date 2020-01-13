# -*- coding: UTF-8 -*-
"""Module for defining report element classes.

"""
import numpy as np
import pandas as pd

from .base import *


__all__ = __features__ = ["Code", "Footer", "Header", "Table", "Section",
                          "Text", "Title"]

HEAD_CSS = "@%(pos)s-left{%(left)s};@%(pos)s-center{%(center)s};@%(pos)s-righ" \
           "t{%(right)s};"


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
    """ Text area report element. """
    def __init__(self, content, size="12", style="normal", color="black",
                 tag="p"):
        self.content = content
        self.tag = tag
        self.style = "font-size:%(size)spx;font-style:%(style)s;color:" \
                     "%(color)s;" % locals()
    
    @output
    def css(self, text=TEXT):
        return 'content:"%(content)s";%(style)s' % self.__dict__
    
    @output
    def html(self, text=TEXT):
        return ('<%(tag)s style="%(style)s">%(content)s</%(tag)s>' % \
                self.__dict__).replace("\n", "<br>")
    
    @output
    def md(self, text=TEXT):
        return self.content


class Code(Text):
    """ Code block report element. """
    def __init__(self, code, size="10", style="normal", color="grey",
                 language=None, hl_lines=None):
        super(Code, self).__init__(code, size, style, color, "pre")
        self.language = language
        self.hl_lines = hl_lines
    
    @output
    def html(self, text=TEXT):
        s = "<pre"
        if self.language:
            s += ' class="%s hljs"' % self.language
        s += ' style="%s">' % self.style
        return s + str(self.content).replace("\n", "<br>") + "</pre>"
    
    @output
    def md(self, text=TEXT):
        s = "```"
        if self.language:
            s += self.language
        if self.hl_lines:
            s += " hl_lines=\"%s\"" % self.hl_lines
        return s + "\n%s\n```" % self.content


class Title(Text):
    """ Title report element. """
    def __init__(self, title, style="normal", color="black", tag="h1"):
        self.content = title
        self.tag = tag
        self.style = "font-style:%(style)s;color:%(color)s;" % locals()
    
    @output
    def md(self, text=TEXT):
        i = self.tag[-1]
        if not i.isdigit():
            raise ValueError("Title tag should be \"h[1-6]\"")
        return "%(prefix)s %(content)s" % {'prefix': "#" * int(i),
                                           'content': self.content}


class Section(Title):
    """ Section report element. """
    def __init__(self, title, style="normal", color="black", tag="h2"):
        super(Section, self).__init__(title, style, color, tag)
