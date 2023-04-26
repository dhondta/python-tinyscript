# -*- coding: UTF-8 -*-
"""Report data transformation functions.

"""
from ...common import lazy_load_module, lazy_object
from ....preimports import inspect, re

lazy_load_module("dicttoxml")
lazy_load_module("json2html", alias="j2h")
lazy_load_module("xmltodict")


__all__ = __features__ = ["dict2html", "dict2xml", "json2html", "json2xml", "report2objects", "xml2dict", "xml2json"]


json2html = dict2html = lazy_object(lambda: j2h.json2html.convert)
json2xml = dict2xml = lazy_object(lambda: dicttoxml.dicttoxml)
xml2json = xml2dict = lazy_object(lambda: xmltodict.parse)


def report2objects(text, header_sep=None, footer_sep=None):
    """ Convert a raw text report (i.e. WPScan-like) to Tinyscript report objects. """
    glob = inspect.currentframe().f_back.f_globals
    o = glob.get('Report', list)()
    if header_sep:
        parts = re.split("[" + re.escape(header_sep) + "]{10,}", text)
        if len(parts) > 1:
            header = parts.pop(0).strip()
            while len(parts) > 0 and header == "":
                header = parts.pop(0).strip()
            if header != "":
                Header = glob.get('Header', None)
                o.append(("Header", header) if Header is None else Header(header))
                text = parts[0]
    if footer_sep:
        parts = re.split("[" + re.escape(footer_sep) + "]{10,}", text)
        if len(parts) > 1:
            footer = parts.pop().strip()
            while len(parts) > 0 and footer == "":
                footer = parts.pop().strip()
            if footer != "":
                Footer = glob.get('Footer', None)
                o.append(("Footer", footer) if Footer is None else Footer(footer))
                text = parts[0]
    blocks = list(re.split(r"(?:\r?\n){2,}", text))
    for i, block in enumerate(blocks):
        block = block.strip()
        lines = re.split(r"\r?\n", block)
        if len(lines) == 1:
            if re.match(r"\[.\]\s", block):
                Subsection = glob.get('Subsection', None)
                o.append(("Subsection", block[4:]) if Subsection is None else Subsection(block[4:]))
            else:
                Section = glob.get('Section', None)
                o.append(("Section", block) if Section is None else Section(block))
        else:
            Text = glob.get('Text', None)
            o.append(("Text", block) if Text is None else Text(block))
    return o

