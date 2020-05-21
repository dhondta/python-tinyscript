# -*- coding: UTF-8 -*-
"""Report data transformation functions.

"""
import re
import xmltodict
from collections import OrderedDict
from dicttoxml import dicttoxml
from json2html import json2html as j2h


__all__ = __features__ = ["dict2html", "dict2xml", "json2html", "json2xml", "report2objects", "xml2dict", "xml2json"]


json2html = dict2html = j2h.convert
json2xml = dict2xml = dicttoxml
xml2json = xml2dict = xmltodict.parse


def report2objects(text, header_sep=None, footer_sep=None):
    """ Convert a raw text report (i.e. WPScan-like) to Tinyscript report objects. """
    o = []
    if header_sep:
        parts = re.split("[" + re.escape(header_sep) + "]{10,}", text)
        if len(parts) > 1:
            header = parts.pop(0).strip()
            while len(parts) > 0 and header == "":
                header = parts.pop(0).strip()
            if header != "":
                o.append(("Header", header))
                text = parts[0]
    if footer_sep:
        parts = re.split("[" + re.escape(footer_sep) + "]{10,}", text)
        if len(parts) > 1:
            footer = parts.pop().strip()
            while len(parts) > 0 and footer == "":
                footer = parts.pop().strip()
            if footer != "":
                o.append(("Footer", footer))
                text = parts[0]
    blocks = list(re.split(r"(?:\r?\n){2,}", text))
    for i, block in enumerate(blocks):
        block = block.strip()
        lines = re.split(r"\r?\n", block)
        if len(lines) == 1:
            if re.match(r"\[.\]\s", block):
                o.append(("Subsection", block[4:]))
            else:
                o.append(("Section", block))
        else:
            o.append(("Text", block))
    return o

