#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = "Alexandre D'Hondt"
__version__ = "1.2"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__training__ = "ZSIS CTF - Trivia - Shining (4 points)"
__doc__ = """
This tool allows to recursively decompress an archive, using multiple Linux decompression
 tools. It currently supports the following tools:
- bzip2
- tar
- unrar
- unxz
- arj
- lzma
- gunzip
- 7za
- unzip
"""
__examples__ = ["test.zip"]


# --------------------- IMPORTS SECTION ---------------------
import shutil
from collections import deque
from subprocess import check_output, PIPE
from tinyscript import *


# -------------------- FUNCTIONS SECTION --------------------
def _log_filetype(filename, magic=None):
    try:
        file_out = check_output(['file', filename]).strip()
        logger.debug(filename if magic is None else \
                     "{} ({})".format(file_out, magic))
    except:
        pass


def decompress(filename):
    logger.info("Decompressing '{}'...".format(filename))
    ft = check_output(['file', filename]).split(':', 1)[1].strip()
    logger.debug(ft)
    if ft.startswith("bzip2 compressed data"):
        old = set(os.listdir("."))
        _ = check_output(["bzip2", "-df", filename], stderr=PIPE)
        return list(set(os.listdir(".")) - old)[0]
    elif ft.startswith("POSIX tar archive"):
        return check_output(["tar", "-xvf", filename]).strip()
    elif ft.startswith("RAR archive data"):
        return check_output(["unrar", "e", filename], stderr=PIPE) \
               .split("Extracting  ", 1)[1].split("        ", 1)[0].strip()
    elif ft.startswith("XZ compressed data"):
        if not filename.endswith(".xz"):
            shutil.move(filename, filename + ".xz")
        _ = check_output(["unxz", "-df", filename + ".xz"], stderr=PIPE)
        return filename
    elif ft.startswith("ARJ archive data"):
        if not filename.endswith(".arj"):
            shutil.move(filename, filename + ".arj")
        return check_output(["arj", "e", filename + ".arj"], stderr=PIPE) \
               .split("Extracting ", 1)[1].split("   ", 1)[0].strip()
    elif ft.startswith("LZMA compressed data"):
        if not filename.endswith(".lzma"):
            shutil.move(filename, filename + ".lzma")
        _ = check_output(["lzma", "-df", filename + ".lzma"], stderr=PIPE)
        return filename
    elif ft.startswith("gzip compressed data"):
        if not filename.endswith(".gz"):
            shutil.move(filename, filename + ".gz")
        _ = check_output(["gunzip", "-df", filename + ".gz"], stderr=PIPE)
        return filename
    elif ft.startswith("7-zip archive data"):
        if not filename.endswith(".7z"):
            shutil.move(filename, filename + ".7z")
        old = set(os.listdir("."))
        _ = check_output(["7za", "e", filename + ".7z"], stderr=PIPE)
        return list(set(os.listdir(".")) - old)[0]
    elif ft.startswith("Zip archive data"):
        if not filename.endswith(".zip"):
            shutil.move(filename, filename + ".zip")
        _ = check_output(["unzip", filename], stderr=PIPE)
        for l in _.split('\n'):
            if "extracting" in l:
                return l.split("extracting:", 1)[1].strip()
    logger.warn("Nothing more to decompress")


# ---------------------- MAIN SECTION -----------------------
if __name__ == '__main__':
    parser.add_argument("archive", help="input archive")
    initialize(globals())
    filename = args.archive
    cleanup = deque([], 2)
    # start recursively decompressing the archive
    while True:
        filename = decompress(filename)
        if filename is None:
            try:  # do not cleanup last decompressed file
                cleanup.pop()
            except:
                pass
            break
        cleanup.append(filename)
        if len(cleanup) == 2:
            os.remove(cleanup.popleft())
    # remove all remaining files
    for i in range(len(cleanup)):
        os.remove(cleanup.pop())
