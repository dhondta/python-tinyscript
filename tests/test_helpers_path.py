#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Pathlib extension tests.

"""
from tempfile import gettempdir
from unittest import TestCase

from tinyscript.helpers.path import *

from utils import *


class TestHelpersPath(TestCase):
    @classmethod
    def setUpClass(cls):
        global FILE, PATH, SPATH, TEST, TPATH1, TPATH2
        TEST = "test_dir"
        PATH = Path(TEST, expand=True, create=True)
        SPATH = PATH.joinpath("test")
        SPATH.mkdir(parents=True, exist_ok=True)
        TPATH1 = TempPath()
        TPATH2 = TempPath(prefix="tinyscript-test_", length=8)
        FILE = PATH.joinpath("test.txt")
        FILE.touch()
        SPATH.joinpath("test.txt").touch()
    
    @classmethod
    def tearDownClass(cls):
        PATH.remove()
        TPATH2.remove()
    
    def test_pathlib_file_extensions(self):
        self.assertEqual(FILE.filename, "test.txt")
        FILE.append_bytes(b"1234")
        self.assertIsInstance(FILE.bytes, bytes)
        self.assertEqual(FILE.size, 4)
        self.assertIsNone(FILE.append_lines("this is", "a test"))
        self.assertEqual(FILE.size, 19)
        self.assertEqual(FILE.text, "1234\nthis is\na test")
        self.assertEqual(FILE.bytes, b"1234\nthis is\na test")
        self.assertIsNone(FILE.reset())
        self.assertEqual(FILE.size, 0)
        self.assertIsNone(FILE.remove())
        self.assertFalse(FILE.exists())
        self.assertIsNone(FILE.touch())
        self.assertEqual(FILE.write_text("this is a test"), 14)
        self.assertEqual(list(FILE.read_lines()), ["this is a test"])
        self.assertEqual(FILE.choice(), FILE)
        self.assertEqual(FILE.generate(), FILE)
        self.assertRaises(TypeError, FILE.append_text, 0)
    
    def test_pathlib_folder_extensions(self):
        self.assertEqual(str(PATH), str(Path(TEST).absolute()))
        self.assertEqual(Path(TEST).child, Path("."))
        self.assertEqual(SPATH.size, 4096)
        self.assertEqual(PATH.size, 4096 + 4096 + 14)  # PATH + SPATH + FILE
        self.assertTrue(PATH.choice(".txt", ".py", ".other").is_samepath(FILE))
        self.assertIsInstance(PATH.generate(), Path)
        self.assertEqual(list(PATH.iterfiles()), [FILE.absolute()])
        self.assertEqual(list(PATH.iterfiles(".py")), [])
        self.assertEqual(list(PATH.iterpubdir()), [SPATH])
        self.assertTrue(TPATH1.exists())
        self.assertEqual(str(TPATH1), gettempdir())
        self.assertTrue(TPATH2.exists())
        self.assertNotEqual(str(TPATH2), gettempdir())
        with TPATH2.tempfile() as tf:
            self.assertTrue(Path(tf.name).exists())
        self.assertNotEqual(len(list(PATH.walk())), 0)
        self.assertNotEqual(len(list(PATH.walk(False))), 0)
        self.assertNotEqual(len(list(PATH.find())), 0)
        self.assertNotEqual(len(list(PATH.find("test"))), 0)
        self.assertNotEqual(len(list(PATH.find("te*"))), 0)
        self.assertEqual(len(list(PATH.find("test2.+", True))), 0)
    
    def test_pathlib_mirrorpath(self):
        PATH2 = Path(TEST + "2", expand=True, create=True)
        PATH2.joinpath("test.txt").touch()
        PATH.joinpath("test2.txt").touch()
        p = MirrorPath(TEST + "2", TEST)
        self.assertTrue(p.joinpath("test").is_symlink())
        self.assertTrue(p.joinpath("test2.txt").is_symlink())
        p.unmirror()
        self.assertFalse(p.joinpath("test").exists())
        self.assertFalse(p.joinpath("test2.txt").exists())
        PATH2.remove()
