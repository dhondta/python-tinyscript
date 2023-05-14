# -*- coding: UTF-8 -*-
"""Module for text-related utility functions.

"""
from gettext import gettext as gt

from .common import lazy_load_module, lazy_object
from .compat import b
from .data.transform.common import str2hex
from .data.types.network import is_email, is_url
from ..preimports import colorful, re, string

lazy_load_module("pypandoc")
lazy_load_module("slugify", alias="_slugify")


__features__ = ["ansi_seq_strip", "gt", "hexdump", "slugify", "txt2blockquote", "txt2bold", "txt2code", "txt2comment",
                "txt2email", "txt2italic", "txt2olist", "txt2paragraph", "txt2preformatted", "txt2title", "txt2ulist",
                "txt2underline", "txt2url", "txt_terminal_render"]
__all__ = __features__ + ["DOCFORMAT_THEME"]

DOCFORMAT = None
DOCFORMAT_THEME = {}
FORMATS = [None, "console", "html", "md", "rst", "textile"]
PRINTABLES = lazy_object(lambda: re.sub(r"\s", "", string.printable))

_indent = lambda t, n: _pline(t, " " * n)
_pline  = lambda t, p, i=False: "\n".join("" if i and l.strip() == "" else p + l for l in t.split("\n"))
_sline  = lambda t: re.sub(r"\n+", " ", t)

slugify = lazy_object(lambda: _slugify.slugify)


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


def ansi_seq_strip(text):
    RE = r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
    try:
        return re.sub(RE, "", text)
    except TypeError:
        return re.sub(b(RE), b"", text)
    


def configure_docformat(glob):
    """ This reconfigures the globally selected documentation format.
    
    :param glob: globals dictionary
    """
    format = glob.get('__docformat__')
    __check(format=format)
    global DOCFORMAT, DOCFORMAT_THEME
    DOCFORMAT, DOCFORMAT_THEME = format, glob.get('DOCFORMAT_THEME', DOCFORMAT_THEME)


def hexdump(data, width=16, first=0, last=0):
    """ This generator converts input data into an hexadecimal dump.
    
    :param data:  data to be dumped
    :param width: width to be displayed in bytes (e.g. 16 will display 8 groups of 2 bytes with the 16 bytes of data)
    :param first: output only the N heading lines of dump
    :param last:  output only the N trailing lines of dump
    """
    n, is_mult = len(data) // width, len(data) % width == 0
    for i in range(0, len(data), width):
        if first > 0 and i // width >= first:
            break
        elif last > 0 and i // width <= n - last - [0, 1][is_mult]:
            continue
        h = str2hex(data[i:i+width])
        h = " ".join(h[j:j+4] for j in range(0, len(h), 4))
        b = "".join(c if c in PRINTABLES else "." for c in data[i:i+width])
        yield "%0.8x:  %s  %s" % (i, h.ljust(width*2+(width//2-1)), b)


def txt_terminal_render(text, format=None, debug=False):
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
    if debug:
        lines = text.split("\n")
        n = len(str(len(lines))) + 2
        for i, l in enumerate(lines):
            print(("{: <%d}{}" % n).format(i, l))
    md = text if format == "md" else pypandoc.convert_text(text, "md", format=format).replace("\\", "")
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
                l = spaces.get(s.group(1), 0)
                line = ARG_REGEX.sub(r"\1{}\4".format(" " * l), line)
            # restore indentations
            else:
                try:
                    line = spaces[line] * " " + line
                except KeyError:
                    pass
            md += line + "\n"
        # 3. links incorrectly rendered after using pandoc
        for link in re.findall("(<(.*?)>)", md):
            md = md.replace(link[0], "[{0}]({1}{0})".format(link[1], ["", "mailto:"][is_email(link[1])]))
    # import only when required to render Markdown in the terminal
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.style import Style
    from rich.theme import Theme
    c = Console(theme=Theme(styles={n: Style(**s) for n, s in DOCFORMAT_THEME.items()}))
    c.begin_capture()
    c.print(Markdown(md))
    return c.end_capture()


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


def _txt_style(text, format="console", bold=False, italic=False, underline=False):
    """ This restyles an input raw text based on the selected format.
    
    :param format:    selected format (one of FORMATS)
    :param bold:      whether the text should be bold
    :param italic:    whether the text should be italic
    :param underline: whether the text should be underline
    """
    format = format or DOCFORMAT
    __check(format=format, bold=bold, italic=italic, underline=underline)
    if format == "console":
        attrs = []
        if bold:
            attrs.append("bold")
        if italic:
            attrs.append("italic")
        if underline:
            attrs.append("underlined")
        if len(attrs) > 0:
            text = str(getattr(colorful, "_".join(attrs))(text))
    elif format == "html":
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
txt2bold = lambda text, format="console": _txt_style(text, format, bold=True)
txt2italic = lambda text, format="console": _txt_style(text, format, italic=True)
txt2underline = lambda text, format="console": _txt_style(text, format, underline=True)


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
        text = _pline(text, "> ")
    elif format == "rst":
        text = _pline(text, "\t")
    elif format == "textile":
        text = "bq.. {}".format(text)
    return text


def txt2code(code, format=None, language=None):
    """ This reformats a raw text to a block of code based on the selected format. """
    format = format or DOCFORMAT
    __check(format=format)
    if format == "html":
        code = "<pre><code{}>{}</code></pre>".format([" class=\"language-%s\"" % language, ""][language is None], code)
    elif format == "md":
        code = "```{}\n{}\n```".format(language or "", code)
    elif format == "rst":
        code = ".. code-block:: {}\n   \n{}".format(language or "raw", _indent(code, 3)) 
    elif format == "textile":
        code = "bc.. {}".format(code)
    return code


def txt2comment(text, format=None, language=None):
    """ This reformats a raw text as a comment based on the selected format. """
    format = format or DOCFORMAT
    __check(format=format)
    if format == "html":
        text = "<!-- {} -->".format(text)
    elif format == "md":
        text = "[//]: # ({})".format(_sline(text))
    elif format == "rst":
        text = ""
    elif format == "textile":
        text = "###. {}".format(_sline(text))
    return text


def txt2email(email, format=None):
    """ This reformats an email to a hyperlink based on the selected format. """
    format = format or DOCFORMAT
    __check(format=format, email=email)
    if format == "html":
        email = "<a href=\"mailto:{0}\">{0}</a>".format(email)
    elif format == "md":
        email = "[{0}](mailto:{0})".format(email)
    elif format == "textile":
        email = "\"{0}\":mailto:{0}".format(email)
    return email


def txt2paragraph(para, format=None):
    """ This reformats a text to a paragraph based on the selected format. """
    format = format or DOCFORMAT
    __check(format=format)
    if format == "html":
        para = "<p>{}</p>".format(para)
    else:
        para = _sline(para)
    return para


def txt2preformatted(text, format=None):
    """ This reformats a raw text as a preformatted text based on the selected format. """
    format = format or DOCFORMAT
    __check(format=format)
    if format == "html":
        text = "<pre>{}</pre>".format(text)
    elif format == "md":
        text = "```\n{}\n```".format(text)
    elif format == "rst":
        text = "::\n   \n{}".format(_indent(text, 3)) 
    elif format == "textile":
        text = "pre.. {}".format(text)
    return text


def txt2title(title, format=None, level=2):
    """ This reformats a text to a title based on the selected format. """
    format = format or DOCFORMAT
    __check(format=format, level=level)
    if format is not None:
        title = title.title()
    if format == "html":
        title = "<h{0}>{1}</h{0}>".format(level, title)
    elif format == "md":
        title = "{} ".format(level * "#") + title
    elif format == "rst":
        title = "{}\n{}".format(title, len(title) * "=-`'~*"[level - 1])
    elif format == "textile":
        title = "h{}. {}".format(level, title)
    return title


def txt2url(text, format=None, url=None):
    """ This reformats a text to a hyperlink based on the selected format. """
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

