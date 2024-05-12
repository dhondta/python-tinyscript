# -*- coding: UTF-8 -*-
"""Module for enhancing json preimport.

"""
import json

from ..helpers import ensure_str


_CACHE = dict()


def dumpc(obj, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None,
          separators=None, default=None, sort_keys=False, **kw):
    """ Serialize ``obj`` as a JSON formatted stream to ``fp`` (a ``.write()``-supporting file-like object. """
    comments = _CACHE.get(id(obj), {})
    indent = comments.get('indent', indent)
    s = json.dumps(obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                   allow_nan=allow_nan, cls=cls, indent=indent, separators=separators, default=default,
                   sort_keys=sort_keys, **kw)
    if indent:
        s, lines = "", s.split("\n")
        for l in lines:
            try:
                ws, c = comments.get('body', {}).get(l.strip().rstrip(","))
                s += f"{l}{' '*ws}#{c}\n"
            except TypeError:
                s += f"{l}\n"
    s = "\n".join(f"{' '*ws}#{c}" for ws, c in comments.get('header', [])) + s
    fp.write(s.encode() if 'b' in fp.mode else s)
json.dumpc = dumpc


def loadc(fp, cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None,
          **kw):
    """ Deserialize ``fp``  (a ``.read()``-supporting file-like object containing a JSON document with comments) to a
         Python object. """
    s, comments, header, indent = [], {}, True, None
    # collect comments from the header then from the body ; keep track of indentation
    for l in ensure_str(fp.read()).split("\n"):
        i = len(l) - len(l.lstrip())
        if i > 0:
            indent = i if indent is None else min(indent, i)
        try:
            l, c = l.split("#", 1)
            ws = len(l) - len(l.rstrip())
        except ValueError:
            c = None
        if header:
            if l.strip() == "":
                if c:
                    comments.setdefault('header', [])
                    comments['header'].append((ws, c.rstrip()))
                    continue
            else:
                header = False
        s.append(l)
        if c:
            comments.setdefault('body', {})
            comments['body'][l.strip().rstrip(",")] = (ws, c.rstrip())
    comments['indent'] = indent
    # now parse the comment-free JSON
    obj = json.loads("\n".join(s), cls=cls, object_hook=object_hook, parse_float=parse_float, parse_int=parse_int,
                     parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
    _CACHE[id(obj)] = comments
    return obj
json.loadc = loadc

