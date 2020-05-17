# -*- coding: UTF-8 -*-
"""Module for text-related utility functions.

"""
import mdv
import re
from gettext import gettext as gt
from pypandoc import convert_text

from .data.types.network import is_email, is_url


__features__ = ["gt", "txt2blockquote", "txt2bold", "txt2email", "txt2italic", "txt2olist", "txt2paragraph",
                "txt2title", "txt2ulist", "txt2underline", "txt2url"]
__all__ = __features__ + ["DOCFORMAT_THEME"]

DOCFORMAT = None
DOCFORMAT_THEME = "Makeup"
FORMATS = [None, "html", "md", "rst", "textile"]


def __check(**kwargs):
    for k, v in kwargs.items():
        if k == 'email' and not is_email(v):
            raise ValueError("Invalid email address")
        elif k == 'format' and v not in FORMATS:
            raise ValueError("Invalid format ; should be one of ({})".format("|".join(map(str, FORMATS))))
        elif k == 'level' and v not in range(1, 7):
            raise ValueError("Invalid title level ; should belong to [1,6]")
        elif k in ['bold', 'italic', 'ordered', 'underline'] and not isinstance(v, bool):
            raise ValueError("Bad boolean value")
        elif k == 'url' and not is_url(v):
            raise ValueError("Invalid URL")


def configure_docformat(glob):
    """ This reconfigures the globally selected documentation format.
    
    :param glob: globals dictionary
    """
    format = glob.get('__docformat__')
    __check(format=format)
    global DOCFORMAT, DOCFORMAT_THEME
    DOCFORMAT = format
    DOCFORMAT_THEME = glob.get('DOCFORMAT_THEME', DOCFORMAT_THEME)


def txt_terminal_render(text, format=None):
    """ This renders input text based on the selected format.
    
    :param format: selected format (one of FORMATS)
    """
    format = format or DOCFORMAT
    __check(format=format)
    if format is None:
        return text
    # collect whitespaces in argument lines and line indentations
    ARG_REGEX = re.compile(r"((?P<h>\-{1,2})[a-z][a-z0-9_]*(?:\s+[A-Z][A-Z_]*)?"
                           r"(?:\,\s+(?P=h)\-[a-z][a-z0-9_]*(?:\s+[A-Z][A-Z_]*)?)?)(\s+)(.*)$")
    spaces = {}
    for line in text.split("\n"):
        s = ARG_REGEX.search(line)
        if s:
            spaces[s.group(1)] = len(s.group(3))
            # e.g. "-v, --verbose" and 10 (whitespaces)
        else:
            tmp = line.lstrip()
            indent = len(line) - len(tmp)
            if indent > 0:
                spaces[tmp.strip()] = indent
    # convert here   
    md = text if format == "md" else convert_text(text, "md", format=format).replace("\\", "")
    if format != "md":
        # bug corrections
        # 1. misaligned metadata fields
        # 2. rectify misaligned arguments' helps
        tmp = md
        md, l = "", 0
        #  collect the maximum field length
        for line in tmp.split("\n"):
            try:
                f, v = line.split(":", 1)
                if f.endswith("default"):
                    raise ValueError
                if re.search(r"(?P<t>[_\*])(.*?)(?P=t)", f):
                    f = "_" + f.strip(" *_") + "_"
                    l = max(l, len(f))
            except ValueError:
                pass
        #  then, remake markdown string
        for line in tmp.split("\n"):
            try:
                f, v = line.split(":", 1)
                if f.endswith("default"):
                    raise ValueError()
                if re.search(r"(?P<t>[_\*])(.*?)(?P=t)", f):
                    f = "_" + f.strip(" *_") + "_"
                    md += ("{: <%d}: {}" % l).format(f, v) + "\n"
                    continue
            except ValueError:
                pass
            # restore spaces between arguments and their help messages
            s = ARG_REGEX.search(line)
            if s:
                l = spaces[s.group(1)]
                line = ARG_REGEX.sub(r"\1{}\4".format(" " * l), line)
            # restore indentations
            else:
                try:
                    line = spaces[line] * " " + line
                except KeyError:
                    pass
            md += line + "\n"
        # 3. links incorrectly rendered with mdv after using pandoc
        for link in re.findall("(<(.*?)>)", md):
            md = md.replace(link[0], "[{0}]({1}{0})".format(link[1], ["", "mailto:"][is_email(link[1])]))
    return mdv.main(md, display_links=True, theme=DOCFORMAT_THEME)


def _txt_list(text, format=None, ordered=False):
    """ This reformats an input raw text list based on the selected format.
    
    :param format:  selected format (one of FORMATS)
    :param ordered: whether the list is ordered or not
    """
    format = format or DOCFORMAT
    __check(format=format, ordered=ordered)
    r = text
    if format == "html":
        r = "<{}l>".format(["u", "o"][ordered])
    elif format in ["md", "rst", "textile"]:
        r = ""
    for line in re.split("\n[\-\*] ", text):
        line = line.lstrip("*- ")
        if format == "html":
            r += "\n<li>{}</li>".format(line)
        elif format in ["md", "rst"]:
            r += "\n- {}".format(line)
        elif format == "textile":
            r += "\n{} {}".format(["*", "#"][ordered], line)
    if format == "html":
        r += "\n</{}l>".format(["u", "o"][ordered])
    return r.strip("\n")
txt2olist = lambda text, format=None: _txt_list(text, format, True)
txt2ulist = lambda text, format=None: _txt_list(text, format)


def _txt_style(text, format=None, bold=False, italic=False, underline=False):
    """ This restyles an input raw text based on the selected format.
    
    :param format:    selected format (one of FORMATS)
    :param bold:      whether the text should be bold
    :param italic:    whether the text should be italic
    :param underline: whether the text should be underline
    """
    format = format or DOCFORMAT
    __check(format=format, bold=bold, italic=italic, underline=underline)
    if format == "html":
        if bold:
            text = "<b>{}</b>".format(text)
        if italic:
            text = "<i>{}</i>".format(text)
        if underline:
            text = "<u>{}</u>".format(text)
    elif format == "md":
        if bold:
            text = "**{}**".format(text)
        if italic:
            text = "_{}_".format(text)
        if underline:  # note: this is a ugly trick using hyperlink
            text = "[{}]()".format(text)
    elif format in ["rst", "textile"]:
        if bold:
            text = "**{}**".format(text)
        if italic:
            text = "*{}*".format(text)
        if underline:
            text = "_{}_".format(text)
    return text
txt2bold = lambda text, format=None: _txt_style(text, format, bold=True)
txt2italic = lambda text, format=None: _txt_style(text, format, italic=True)
txt2underline = lambda text, format=None: _txt_style(text, format, underline=True)


def txt2blockquote(text, format=None):
    """ This reformats a text to a block quote based on the selected format.
    
    :param format: selected format (one of FORMATS)
    """
    format = format or DOCFORMAT
    __check(format=format)
    text = text.strip("\n")
    if format == "html":
        text = "<blockquote>{}</blockquote>".format(text.strip("\n"))
    elif format == "md":
        text = "\n".join("> {}".format(line) for line in text.splitlines())
    elif format == "rst":
        text = "\n".join("\t{}".format(line) for line in text.splitlines())
    elif format == "textile":
        text = "\n".join("" if line.strip() == "" else "bq. " + line for line in text.splitlines())
    return text


def txt2email(text, format=None):
    """ This reformats an email to a hyperlink based on the selected format.
    
    :param format: selected format (one of FORMATS)
    :param text:   email address
    """
    format = format or DOCFORMAT
    __check(format=format, email=text)
    if format == "html":
        text = "<a href=\"mailto:{0}\">{0}</a>".format(text)
    elif format == "md":
        text = "[{0}](mailto:{0})".format(text)
    elif format == "textile":
        text = "\"{0}\":mailto:{0}".format(text)
    return text


def txt2paragraph(text, format=None):
    """ This reformats a text to a paragraph based on the selected format.
    
    :param format: selected format (one of FORMATS)
    """
    format = format or DOCFORMAT
    __check(format=format)
    if format == "html":
        text = "<p>{}</p>".format(text)
    elif format in ["rst", "textile"]:
        text = "\n" + text
    return text


def txt2title(text, format=None, level=2):
    """ This reformats a text to a title based on the selected format.
    
    :param format: selected format (one of FORMATS)
    :param level:  title level
    """
    format = format or DOCFORMAT
    __check(format=format, level=level)
    if format is not None:
        text = text.title()
    if format == "html":
        text = "<h{0}>{1}</h{0}>".format(level, text)
    elif format == "md":
        text = "{} ".format(level * "#") + text
    elif format == "rst":
        text = "{}\n{}".format(text, len(text) * "=-`'~*"[level - 1])
    elif format == "textile":
        text = "h{}. {}".format(level, text)
    return text


def txt2url(text, format=None, url=None):
    """ This reformats a text to a hyperlink based on the selected format.
    
    :param format: selected format (one of FORMATS)
    :param url:    URL
    """
    format = format or DOCFORMAT
    if url is None:
        __check(format=format, url=text)
        url = text
    else:
        __check(format=format, url=url)
    if format == "html":
        text = "<a href=\"{}\">{}</a>".format(url, text)
    elif format == "md":
        text = "[{}]({})".format(text, url)
    elif format == "textile":
        if text == url:
            text = "$"
        text = "\"{}\":{}".format(text, url)
    return text

