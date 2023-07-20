#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from tinyscript import *
from tinyscript.helpers import copyright, file_mode, license, url, urlparse, Path
from tinyscript.template import new as new_script, TARGETS

from tinyscript.__info__ import __author__, __copyright__, __email__, __license__, __version__


__description__ = "Tiny Scripts Manager"
__examples__ = [
    "add-source https://example.com/scripts.list --fetch",
    "install wlf",
    "install stegopit --force",
    "install stegopvd --mode 666",
    "new test",
    "new my-script -t pybots.HTTPBot",
    "remove-source https://example.com/scripts.list",
    "search '.*test.*' --extended",
    "update",
    "update -s https://example.com/scripts.list",
]
__doc__      = """
This tool allows to quickly create a new Tinyscript script/tool from a template.
"""


BIN = Path("~/.bin", expand=True, create=True)
CACHE = ts.ConfigPath("tinyscript", create=True).joinpath("cache.json")
DUNDERS = ["__author__", "__email__", "__version__", "__copyright__", "__license__"]
SOURCES = ts.ConfigPath("tinyscript").joinpath("sources.conf")
if not SOURCES.exists():
    SOURCES.write_text("https://raw.githubusercontent.com/dhondta/python-tinyscript/main/docs/scripts.list")
TIMEOUT = 2


__add_fetch = lambda p, **kw: p.add_argument("-f", "--fetch", action="store_true", help="fetch the target URL", **kw)
__add_name = lambda p, **kw: p.add_argument("name", type=ts.str_matches(r"^([0-9a-z]+[-_]+)?[0-9a-z]+$", re.I),
                                            help="name of the script (without the .py extension)", **kw)
__add_src = lambda p, **kw: p.add_argument("-s", "--source", type=url, help="specific source for searching", **kw)
__add_url = lambda p, **kx: p.add_argument("url", type=url, help="URL of a list of scripts")
__version = lambda s: list(map(int, s.split(".")))


def __download(url, **kw):
    try:
        with requests.get(url, allow_redirects=True, stream=True, timeout=TIMEOUT, **kw) as resp:
            resp.raise_for_status()
            content = b"".join(chunk for chunk in resp.iter_content(chunk_size=4096)).decode()
            return content, _parse_metadata(content)
    except requests.exceptions.Timeout:
        logger.error("Request for '%s' timed out" % url)
    except requests.exceptions.TooManyRedirects:
        logger.error("Too many redirects for '%s'" % url)
    except requests.exceptions.RequestException as e:
        resp = e.response
        if resp:
            logger.error("'%s' cannot be opened (status code: %d - %s)" % (url, resp.status_code, resp.reason))
        else:
            logger.error(str(e))
    return None, {}


def _fetch_source(target):
    target = target.strip(" \r\n")
    logger.info("Fetching source '%s'..." % target)
    CACHE.touch()
    with CACHE.open() as f:
        try:
            cache = json.load(f)
        except json.decoder.JSONDecodeError:
            cache = {}
    cache.setdefault(target, {})
    content, _ = __download(target)
    if content is None:
        cache.pop(target, None)
        return False
    for l in content.split("\n"):
        l = l.strip()
        if l == "" or l.startswith("#"):
            continue
        try:
            link, alias = l.split("|")
        except ValueError:
            link, alias = l, Path(urlparse(l).path).stem
        cache[target][alias] = {'link': link}
    _update_cache(cache)
    return True


def _get_sources_list(fetch=False):
    r = []
    if SOURCES.exists():
        with SOURCES.open() as f:
            for l in f:
                source = l.strip(" \r\n")
                if source == "" or source.startswith("#"):
                    continue
                if fetch:
                    logger.info("Fetching source '%s'..." % source)
                    __download(source)
                r.append(source)
    return r


def _iter_sources(source=None):
    if CACHE.exists():
        with CACHE.open() as f:
            cache = json.load(f)
        if source:
            try:
                yield cache, source, cache[source]
            except KeyError:
                logger.error("Source '%s' does not exist" % source)
        else:
            for source, scripts in cache.items():
                yield cache, source, scripts
    else:
        logger.warning("No cache available ; please use 'tinyscript update' to get script links from sources")


def _parse_metadata(content):
    meta = {}
    for l in content.split("\n"):
        m = re.match(r"__([a-z]+)__", l)
        if m:
            meta[m.group(1)] = l.split("=", 1)[1].strip(" \"")
    return meta


def _update_cache(cache):
    with CACHE.open('w') as f:
        json.dump(cache, f, indent=2)


def main():
    commands = parser.add_subparsers(dest="command", help="command to be executed")
    with commands.add_parser("add-source", help="add a source for installing scripts") as addsrc:
        __add_url(addsrc)
        __add_fetch(addsrc)
    with commands.add_parser("install", help="install a script from a source") as install:
        __add_name(install, note="will install the first seen occurrence from sources if no source is specified")
        install.add_argument("-f", "--force", action="store_true", help="overwrite the script if it exists")
        install.add_argument("-m", "--mode", type=file_mode, default="750", help="custom file mode")
        __add_src(install)
    with commands.add_parser("new", help="make a new script") as new:
        __add_name(new)
        new.add_argument("-t", "--target", choices=TARGETS.keys(), help="target to be created")
    with commands.add_parser("remove-source", help="remove a source of scripts") as remsrc:
        __add_url(remsrc)
    with commands.add_parser("search", help="search for available script among the locally cached sources") as search:
        search.add_argument("pattern", nargs="?", default=".*", help="pattern of script name")
        search.add_argument("-e", "--extended", action="store_true", help="search among the links too")
        __add_fetch(search)
        __add_src(search)
    with commands.add_parser("update", help="update the list of publicly available scripts") as update:
        update.add_argument("-s", "--source", nargs="*", type=url, help="set a source URL for a list of scripts")
    initialize(noargs_action="wizard")
    if args.command =="add-source":
        s, sources = args.url, _get_sources_list()
        if not args.fetch or args.fetch and _fetch_source(s):
            if s in sources:
                logger.warning("Source '%s' already exists" % s)
            else:
                with SOURCES.open('a') as f:
                    f.write(s)
                logger.info("Added source '%s'" % s)
    elif args.command == "install":
        script = BIN.joinpath(args.name)
        if script.exists() and not args.force:
            meta = _parse_metadata(script.read_text())
            v = meta.get('version')
            logger.warning(("Script '%s' already exists" % args.name) + [" (version: %s)" % v, ""][v is None])
        else:
            local_v = __version(_parse_metadata(script.read_text()).get('version') if script.exists() else "0.0.0")
            for cache, source, scripts in _iter_sources(args.source):
                if args.name in scripts.keys():
                    link = scripts[args.name]['link']
                    status = ["installed", "updated"][script.exists()]
                    content, meta = __download(link)
                    if content is None:
                        continue
                    v = __version(meta.get('version', "0.0.0"))
                    if v != (0, 0, 0) and v >= local_v:
                        script.write_text(content)
                        cache[source][args.name].update(meta)
                        script.chmod(args.mode)
                        logger.info("Script '%s' %s" % (args.name, status))
                    else:
                        logger.warning("Remote script has a lower version, hence not updated")
                    break
            _update_cache(cache)
    elif args.command == "new":
        new_script(args.name, args.target)
    elif args.command == "remove-source":
        s = args.url
        with SOURCES.open('r+') as f:
            sources = f.readlines()
            l = len(sources)
            new = [_ for _ in sources if _.strip(" #\r\n") != s]
            if l == len(new):
                logger.warning("'%s' not found" % s)
            else:
                f.seek(0)
                f.truncate()
                f.writelines(new)
                logger.info("Removed source '%s'" % s)
    elif args.command == "search":
        for cache, source, scripts in _iter_sources(args.source):
            for name, data in scripts.items():
                link = data['link']
                if re.search(args.pattern, name) or args.extended and re.search(args.pattern, link):
                    print("%s\n  URL   : %s\n  Source: %s" % (name, link, source))
                    if args.fetch:
                        _, meta = __download(link, headers={'Range': "bytes=32-1024"})
                        cache[source][name] = {'link': link}
                        cache[source][name].update(meta)
                        _update_cache(cache)
                    meta = {k: v for k, v in cache[source][name].items() if k != 'link'}
                    dunders = [d.strip("_") for d in DUNDERS if d.strip("_") in meta.keys()]
                    if len(dunders) > 0:
                        print("  Info  :")
                        maxl, s = max(map(len, dunders)), ""
                        for i, k in enumerate(dunders):
                            v = meta[k]
                            if k == "author":
                                s += "    - " + ("{: <%d}: {}" % maxl).format(k.strip('_').capitalize(), v) + \
                                     ["\n", ""]["email" in dunders]
                            elif k == "email":
                                if "author" in dunders:
                                    s += " (%s)\n" % v
                            else:
                                func = globals().get(k, lambda s: s)
                                try:
                                    v = ast.literal_eval(v)
                                except:
                                    pass
                                v = func(*v) if isinstance(v, tuple) else func(v)
                                s += "    - " + ("{: <%d}: {}" % maxl).format(k.strip('_').capitalize(), v) + "\n"
                        print(s)
    elif args.command == "update":
        if SOURCES.exists():
            with SOURCES.open() as f:
                for l in f:
                    source = l.strip(" \r\n")
                    if source == "" or source.startswith("#"):
                        continue
                    _fetch_source(l)
        else:
            logger.warning("'%s' does not exist" % SOURCES)

