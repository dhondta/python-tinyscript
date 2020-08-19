# -*- coding: UTF-8 -*-
"""Module for defining report element classes.

"""
from inspect import stack

from .base import *
from ..helpers.data.transform import json2html, json2xml


__all__ = __features__ = ["Blockquote", "Code", "Data", "Footer", "Header", "Image", "List", "Rule", "Section",
                          "Subsection", "Table", "Text", "Title"]

HEAD_CSS = "@%(pos)s-left{%(left)s};@%(pos)s-center{%(center)s};@%(pos)s-right{%(right)s};"


class Data(Element):
    """ This class represents a data dictionary.
    
    :param data: data dictionary
    """
    filename = "data"
    
    def __init__(self, data, **kwargs):
        super(Data, self).__init__(**kwargs)
        if not isinstance(data, (dict, list, set, tuple)):
            raise ValueError("'data' argument shall be a dictionary or a list (got {})".format(type(data).__name__))
        self._data = data
    
    @output
    def html(self, indent=4, text=TEXT):
        return json2html(self.data).replace("\"", "'")
    
    @output
    def json(self, text=TEXT):
        return self.data
    
    @output
    def xml(self, indent=2, text=TEXT):
        return json2xml(self.data)


class Footer(Element):
    """ This class represents the footer of a report.
    
    :param left:   left-side section of the footer
    :param center: center section of the footer
    :param right:  right-side section of the footer
    """
    _style = {'size': 9, 'style': "normal", 'color': "black"}
    pos = "bottom"
    
    def __init__(self, left="", center="", right="", **kwargs):
        super(Footer, self).__init__(**kwargs)
        self.pos = self.__class__.pos
        if self.pos == "bottom" and center == "":
            center = "\" counter(page) \"/\" counter(pages) \""
        self.data = {'left': left, 'center': center, 'right': right}
        d = {k: v for k, v in self.data.items()}
        d.update(pos=self.pos)
        self.css = HEAD_CSS % d
    
    @output
    def xml(self, indent=2, text=TEXT):
        ind, nl = self._set_indent(indent)
        r = []
        for attr in ["left", "center", "right"]:
            if len(self.data[attr]) > 0:
                r.append(ind + "<%(tag)s>%(content)s</%(tag)s>" % {'tag': attr, 'content': self.data[attr]})
        if len(r) > 0:
            r = ["<%s>" % self.name] + r + ["</%s>" % self.name]
        return nl.join(r)


class Header(Footer):
    """ This class represents the header of a report.
    
    :param left:   left-side section of the header
    :param center: center section of the header
    :param right:  right-side section of the header
    """
    pos = "top"


class Image(Element):
    """ This class represents an image.
    
    :param source: image's source path
    """
    def __init__(self, source, title=None, alt=None, width=None, height=None, **kwargs):
        super(Image, self).__init__(**kwargs)
        self.data = {'source': source, 'title': title or "", 'alt': alt or "",
                     'width': width or "", 'height': height or ""}
    
    @output
    def html(self, indent=4, text=TEXT):
        img = "<img src='%s'" % self.data['source']
        for k in ['title', 'width', 'height']:
            v = self.data.get(k)
            if v:
                img += " %s='%s'" % (k, v)
        return img + "/>"
    
    @output
    def md(self, text=TEXT):
        return "![%(title)s](%(source)s)" % self.data
    
    @output
    def rst(self, text=TEXT):
        s = ".. image:: %(source)s" % self.data
        for attr, val in self.data.items():
            if attr != "source" and val:
                s += "\n    :%s: %s" % (attr, val)
        return s
    
    @output
    def xml(self, indent=2, text=TEXT):
        ind, nl = self._set_indent(indent)
        xml = "<%(name)s>{0}{1}{0}</%(name)s>" % self.__dict__
        attrs = ind + "<source>%s</source>" % self.data['source']
        for k in ['title', 'width', 'height']:
            v = self.data.get(k)
            if v:
                attrs += nl + ind + "<%s>" % k + v + "</%s>" % k
        return xml.format(nl, attrs)


class List(Element):
    """ This class represents a list of items, ordered or not.
    
    :param items:   list's items
    :param ordered: whether the list is to be ordered or not
    """
    def __init__(self, *items, **kwargs):
        super(List, self).__init__(**kwargs)
        self._data = items
        self.ordered = kwargs.get('ordered', False)
        self.tag = ["ul", "ol"][self.ordered]
    
    @output
    def csv(self, sep=',', text=TEXT):
        return "\n".join(self.data)
    
    @output
    def html(self, indent=4, text=TEXT):
        ind, nl = self._set_indent(indent)
        s = "<%s" % self.tag
        if self.style:
            s += " style='%s'" % self.style
        s += ">" + nl
        for i in self.data:
            s += ind + "<li>%s</li>" % i + nl
        return s + "</%s>" % self.tag
    
    @output
    def md(self, text=TEXT):
        return "\n".join("%s %s" % (["-", "%d." % (n+1)][self.ordered], i) for n, i in enumerate(self.data))
    rst = md
    
    @output
    def xml(self, indent=2, text=TEXT):
        ind, nl = self._set_indent(indent)
        xml = "<%(name)s>{0}{1}{0}</%(name)s>" % self.__dict__
        return xml.format(nl, "\n".join(ind + "<item>%s</item>" % i for i in self.data))


class Rule(Element):
    """ This class represents an horizontal rule. """    
    @output
    def html(self, indent=4, text=TEXT):
        ind, nl = self._set_indent(indent)
        s = "<hr"
        if self.style:
            s += " style='%s'" % self.style
        return s + ">"
    
    @output
    def json(self, text=TEXT):
        return {}
    
    @output
    def md(self, text=TEXT, n=5, char="-"):
        return n * char
    rst = md
    
    @output
    def xml(self, indent=2, text=TEXT):
        return ""


class Table(Element):
    """ This class represents a table.
    
    :param data:           table data
    :param column_headers: list of column headers or "indices" or None ; if "indices", it is replaced accordingly
    :param row_headers:    list of row headers or "indices" or None ; if "indices", it is replaced accordingly
    :param column_footers: list of column footers or None
    :param flt_fmt:        float format to be displayed when generating the output
    """
    filename = "table"
    
    def __init__(self, data, column_headers="indices", row_headers=None, column_footers=None, title=None,
                 flt_fmt="%.2g", **kwargs):
        super(Table, self).__init__(**kwargs)
        self.index = row_headers == "indices"
        self.column_headers = list(map(str, range(len(data[0])))) if column_headers == "indices" else column_headers
        self.column_footers = column_footers
        self.row_headers = list(map(str, range(len(data)))) if row_headers == "indices" else row_headers
        if self.row_headers and len(data) != len(self.row_headers):
            raise ValueError("Bad row headers length")
        if self.column_headers and len(data[0]) != len(self.column_headers):
            raise ValueError("Bad column headers length")
        if self.column_headers is not None and self.row_headers is not None:
            self.column_headers = [""] + self.column_headers
        self._data = data
        self.float_fmt = flt_fmt
        self.title = title or ""
    
    def _format(self, data):
        d = []
        output_format = stack()[1][3]  # get the calling output format method name from the stack
        for i, row in enumerate(data):
            row = list(map(lambda x: self.float_fmt % x if isinstance(x, float) else str(x), row))
            if self.row_headers is not None:
                row.insert(0, Element.format_data(self.row_headers[i], output_format))
            d.append(row)
        return d
    
    @output
    def csv(self, sep=',', text=TEXT):
        r = "" if self.column_headers is None else sep.join(self.column_headers)
        for row in self._format(self.data):
            r += "\n" + sep.join(row)
        return r
    
    @output
    def html(self, indent=4, text=TEXT):
        ind, nl = self._set_indent(indent)
        t = "<table id='%s'" % self.name
        if self.style:
            t += " style='%s'" % self.style
        r = [t + ">"]
        if self.column_headers is not None:
            r.append(ind + "<thead>")
            r.append(2 * ind + "<tr>")
            for h in self.column_headers:
                r.append(3 * ind + "<th>%s</th>" % h)
            r.append(2 * ind + "</tr>")
            r.append(ind + "</thead>")
        r.append(ind + "<tbody>")
        for row in self._format(self.data):
            r.append(2 * ind + "<tr>")
            for i, v in enumerate(row):
                xml = "<{0}>%s</{0}>".format(["td", "th"][i == 0 and self.row_headers is not None])
                r.append(3 * ind + xml % v)
            r.append(2 * ind + "</tr>")
        r.append(ind + "</tbody>")
        if self.column_footers is not None:
            r.append(ind + "<tfoot>")
            r.append(2 * ind + "<tr>")
            for h in self.column_footers:
                r.append(3 * ind + "<th>%s</th>" % h)
            r.append(2 * ind + "</tr>")
            r.append(ind + "</tfoot>")
        r.append("</table>")
        return nl.join(r)
    
    @output
    def md(self, float_format="%.2g", text=TEXT):
        r = [" | ".join(self.column_headers or list(map(str, range(len(self.data[0])))))]
        r.append(" | ".join("---" for i in range(len(self.data[0]))))
        for row in self._format(self.data):
            r.append(" | ".join(row))
        if self.column_footers is not None:
            r.append(" | ".join(map(lambda x: "**%s**" % x, self.column_footers)))
        return "\n".join(r)
    
    @output
    def rst(self, float_format="%.2g", text=TEXT):
        def fmt(v):
            try:
                float(v)
                return str(v)
            except:
                return "\"{}\"".format(v)
        
        r = ".. csv-table: %s\n" % self.title
        if self.column_headers:
            r += "    :header: %s\n" % ", ".join(fmt(v) for v in self.column_headers)
        for row in self._format(self.data):
            r += "\n    " + ", ".join(fmt(v) for v in row)
        return r
    
    @output
    def xml(self, indent=2, text=TEXT):
        ind, nl = self._set_indent(indent)
        r = ["<%s>" % self.name]
        for row in self.data:
            r.append(ind + "<row>")
            for i, v in enumerate(row):
                if self.column_headers is None:
                    n = ""
                elif i == 0 and self.index:
                    n = ' name="index"'
                else:
                    n = ' name="%s"' % self.column_headers[i]
                r.append(2 * ind + "<field%s>%s</field>" % (n, v))
            r.append(ind + "</row>")
        if self.column_footers is not None:
            r.append(ind + "<footer>")
            for h in self.column_footers:
                r.append(2 * ind + "<field>%s</field>" % h)
            r.append(ind + "</footer>")
        r.append("</%s>" % self.name)
        return nl.join(r)


class Text(Element):
    """ Text area report element.
    
    :param content: text content
    :param tag:     HTML tag to be used
    """
    def __init__(self, content, tag="p", **kwargs):
        super(Text, self).__init__(**kwargs)
        self._data = content
        self.tag = tag
    
    @output
    def html(self, indent=4, text=TEXT):
        h = "<%s" % self.tag
        if self.style:
            h += " style='%s'" % self.style
        h += ">%s</%s>" % (self.data, self.tag)
        return h.replace("\n", "<br>")
    
    @output
    def md(self, text=TEXT):
        return self.data
    rst = md


class Blockquote(Text):
    """ Text area report element.
    
    :param content: text content
    """
    def __init__(self, content, **kwargs):
        super(Text, self).__init__(**kwargs)
        self.data = content
        self.tag = "blockquote"
    
    @output
    def md(self, text=TEXT):
        return "\n".join("> " + l for l in self.data.split("\n"))
    
    @output
    def rst(self, text=TEXT):
        return "\n".join("    " + l for l in self.data.split("\n"))


class Code(Text):
    """ Code block report element.
    
    :param code:     code content
    :param language: code's language
    param hl_lines:  lines to be highlighted
    """
    _style = {'size': 10, 'style': "normal", 'color': "grey"}
    
    def __init__(self, code, language=None, hl_lines=None, **kwargs):
        super(Code, self).__init__(code, "pre", **kwargs)
        self.language = language
        self.hl_lines = hl_lines
    
    @output
    def html(self, indent=4, text=TEXT):
        s = "<pre"
        if self.language:
            s += " class='%s hljs'" % self.language
        if self.style:
            s += " style='%s'>" % self.style
        return s + str(self.data).replace("\n", "<br>") + "</pre>"
    
    @output
    def md(self, text=TEXT):
        s = "```"
        if self.language:
            s += self.language
        if self.hl_lines:
            s += " hl_lines=\"%s\"" % self.hl_lines
        return s + "\n%s\n```" % self.data
    
    @output
    def rst(self, text=TEXT):
        s = ".. code-block:"
        if self.language:
            s += " %s" + self.language
        s += "\n    "
        for l in self.data.split("\n"):
            s += "\n    " + l
        return s


class Title(Text):
    """ Title report element.
    
    :param title: title content
    :param tag:   HTML tag to be used
    """
    _style = {}
    
    def __init__(self, title, tag="h1", **kwargs):
        if tag not in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            raise ValueError("Title tag should be \"h[1-6]\", not \"{}\"".format(tag))
        super(Title, self).__init__(title, tag, **kwargs)
    
    @output
    def md(self, text=TEXT):
        return "%(prefix)s %(content)s" % {'prefix': "#" * int(self.tag[-1]), 'content': self.data}
    
    @output
    def rst(self, text=TEXT):
        i = int(self.tag[-1])
        if i <= 2:
            return "%(line)s\n%(content)s\n%(line)s" % {'line': len(self.data) * "#*"[i-1], 'content': self.data}
        elif i <= 6:
            return "%(content)s\n%(line)s" % {'line': len(self.data) * "=-~^"[i-1], 'content': self.data}


class Section(Title):
    """ Section report element.
    
    :param title: title content
    :param tag:   HTML tag to be used
    """
    def __init__(self, title, tag="h2", **kwargs):
        super(Section, self).__init__(title, tag, **kwargs)


class Subsection(Title):
    """ Subsection report element.
    
    :param title: title content
    :param tag:   HTML tag to be used
    """
    def __init__(self, title, tag="h3", **kwargs):
        super(Subsection, self).__init__(title, tag, **kwargs)

