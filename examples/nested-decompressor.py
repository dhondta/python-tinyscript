#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__doc__ = """
This tool allows to recursively decompress an archive according to various
 formats relying on many Linux decompression tools.
"""

import glob
import shutil
from subprocess import check_output, PIPE
from tinyscript import *


TMP_DIR = ".tmp"


def decompress(f):
    logger.info("Decompressing '{}'...".format(f))
    ft = check_output(['file', f]).split(':', 1)[1].strip()
    logger.debug(ft)
    if ft.startswith("bzip2 compressed data"):
        old = set(os.listdir("."))
        _ = check_output(["bzip2", "-df", f], stderr=PIPE)
        return False, list(set(os.listdir(".")) - old)[0]
    elif ft.startswith("POSIX tar archive"):
        return False, check_output(["tar", "-xvf", f]).strip()
    elif ft.startswith("RAR archive data"):
        return False, check_output(["unrar", "e", f], stderr=PIPE) \
               .split("Extracting  ", 1)[1].split("        ", 1)[0].strip()
    elif ft.startswith("XZ compressed data"):
        if not f.endswith(".xz"):
            shutil.move(f, f + ".xz")
        _ = check_output(["unxz", "-df", f + ".xz"], stderr=PIPE)
        return False, f
    elif ft.startswith("ARJ archive data"):
        if not f.endswith(".arj"):
            shutil.move(f, f + ".arj")
        return False, check_output(["arj", "e", f + ".arj"], \
                stderr=PIPE).split("Extracting ", 1)[1].split("   ", 1)[0].strip()
    elif ft.startswith("LZMA compressed data"):
        if not f.endswith(".lzma"):
            shutil.move(f, f + ".lzma")
        _ = check_output(["lzma", "-df", f + ".lzma"], stderr=PIPE)
        return False, f
    elif ft.startswith("gzip compressed data"):
        if not f.endswith(".gz"):
            shutil.move(f, f + ".gz")
        _ = check_output(["gunzip", "-df", f + ".gz"], stderr=PIPE)
        return False, f
    elif ft.startswith("7-zip archive data"):
        if not f.endswith(".7z"):
            shutil.move(f, f + ".7z")
        old = set(os.listdir("."))
        _ = check_output(["7za", "e", f + ".7z", "-y"], stderr=PIPE)
        return False, list(set(os.listdir(".")) - old)[0]
    logger.warn("Nothing more to decompress")
    return True, f


if __name__ == '__main__':
    parser.add_argument("archive", help="input archive")
    initialize(globals())
    os.makedirs(TMP_DIR)
    shutil.copy(args.archive, os.path.join(TMP_DIR, args.archive))
    _ = os.getcwd()
    os.chdir(TMP_DIR)
    stop, f = False, args.archive
    while not stop:
        stop, f = decompress(f)
    os.chdir(_)
    shutil.move(os.path.join(TMP_DIR, f), ".")
    shutil.rmtree(TMP_DIR)
