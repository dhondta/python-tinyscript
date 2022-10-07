#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Pathlib2 extension tests.

"""
import py_compile
from tempfile import gettempdir
from unittest import TestCase

from tinyscript.helpers.path import *

from utils import *


class TestHelpersPath(TestCase):
    @classmethod
    def setUpClass(cls):
        global FILE, FILE2, MODULE, NOTEX, PATH, SPATH, TEST, TPATH1, TPATH2
        TEST = "test_dir"
        PATH = Path(TEST, expand=True, create=True)
        SPATH = PATH.joinpath("test")
        SPATH.mkdir(parents=True, exist_ok=True)
        TPATH1 = TempPath()
        TPATH2 = TempPath(prefix="tinyscript-test_", length=8)
        m = TPATH2.joinpath("modules")
        m.mkdir()
        f = Path(str(m.joinpath("test1.py")), touch=True)
        MODULE = m.joinpath("test2.py")
        f.write_text("#!/usr/bin/env python\nimport os")
        f.write_bytes(b"#!/usr/bin/env python\nimport os")
        py_compile.compile(str(f))
        (m.joinpath("__pycache__") if PYTHON3 else f.dirname).joinpath("not-cached.pyc").touch()
        MODULE.write_text("#!/usr/bin/env python\nimport os\n\nclass Test(object):\n   pass\n\n"
                          "def test(): pass #TODO: test")
        FILE = PATH.joinpath("test.txt")
        FILE.touch()
        FILE2 = PATH.joinpath("test2.txt")
        SPATH.joinpath("test.txt").touch()
        NOTEX = Path("DOES_NOT_EXIST")
    
    @classmethod
    def tearDownClass(cls):
        PATH.remove()
        TPATH2.remove()
    
    def test_file_extensions(self):
        self.assertRaises(ValueError, Path, PATH.joinpath("test1.py"), create=True, touch=True)
        self.assertRaises(OSError, NOTEX.remove)
        self.assertIsNone(NOTEX.remove(error=False))
        self.assertEqual(FILE.filename, "test.txt")
        FILE.append_bytes(b"1234")
        self.assertIsNotNone(FILE.permissions)
        self.assertIsInstance(FILE.bytes, bytes)
        self.assertEqual(FILE.size, 4)
        self.assertIsNone(FILE.append_lines("this is", "a test"))
        self.assertEqual(FILE.size, [19, 21][WINDOWS])  # take \r\n into account
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
        self.assertTrue(FILE.is_under(FILE))
        self.assertTrue(FILE.copy(FILE2).is_file())
        FILE2.remove()
        self.assertFalse(FILE2.copy(FILE).is_file())
    
    def test_folder_extensions(self):
        self.assertEqual(str(PATH), str(Path(TEST).absolute()))
        self.assertEqual(Path(TEST).child, Path("."))
        self.assertEqual(SPATH.size, 4096)
        self.assertEqual(PATH.size, [4096 + 4096 + 14, 8213][WINDOWS])  # PATH + SPATH + FILE
        self.assertTrue(PATH.choice(".txt", ".py", ".other").is_samepath(FILE))
        self.assertIsInstance(PATH.generate(), Path)
        self.assertEqual(list(PATH.iterfiles()), [FILE.absolute()])
        self.assertEqual(list(PATH.iterfiles(".py")), [])
        self.assertEqual(list(PATH.iterpubdir()), [SPATH])
        self.assertNotEqual(len(list(PATH.walk())), 0)
        self.assertNotEqual(len(list(PATH.walk(False))), 0)
        self.assertNotEqual(len(list(PATH.find())), 0)
        self.assertNotEqual(len(list(PATH.find("test"))), 0)
        self.assertNotEqual(len(list(PATH.find("te*"))), 0)
        self.assertEqual(len(list(PATH.find("test2.+", True))), 0)
    
    def test_config_path(self):
        PATH = ConfigPath("test-app", file=True)
        self.assertTrue(str(PATH).endswith("test-app.conf"))
    
    def test_credentials_path(self):
        PATH1 = CredentialsPath("test_creds")
        self.assertEqual(PATH1.id, "")
        self.assertEqual(PATH1.secret, "")
        with mock_patch("tinyscript.helpers.inputs.std_input", return_value="test"), \
             mock_patch("getpass.getpass", return_value=""):
            PATH1.ask()
        self.assertEqual(PATH1.id, "test")
        self.assertEqual(PATH1.secret, "")
        with mock_patch("tinyscript.helpers.inputs.std_input", return_value="test"), \
             mock_patch("getpass.getpass", return_value=""):
            self.assertRaises(ValueError, PATH1.ask, ("Identifier:", r"test\d+"))
        self.assertEqual(PATH1.id, "test")
        with mock_patch("tinyscript.helpers.inputs.std_input", return_value="test1"), \
             mock_patch("getpass.getpass", return_value="test"):
            self.assertRaises(ValueError, PATH1.ask, ("ID:", r"test\d+"), ("Secret:", r"[a-z]+\d+"))
        self.assertEqual(PATH1.id, "test1")
        self.assertEqual(PATH1.secret, "")
        with mock_patch("tinyscript.helpers.inputs.std_input", return_value="test1"), \
             mock_patch("getpass.getpass", return_value="test1"):
            PATH1.ask(("ID:", r"test\d+"), ("Secret:", r"[a-z]+\d+"))
        self.assertEqual(PATH1.id, "test1")
        self.assertEqual(PATH1.secret, "test1")
        self.assertIsNone(PATH1.save())
        PATH2 = CredentialsPath("test_creds")
        self.assertEqual(PATH2.id, "test1")
        self.assertEqual(PATH2.secret, "test1")
        PATH2.remove()
        PATH3 = CredentialsPath("test_creds", id="test2", secret="test2")
        self.assertEqual(PATH3.id, "test2")
        self.assertEqual(PATH3.secret, "test2")
        self.assertRaises(ValueError, PATH3.load, "t")  # bad delimiter
        self.assertRaises(ValueError, PATH3.save, "t")
        PATH3.remove()
        PATH4 = CredentialsPath("test_creds")
        PATH4.save()  # id and secret are "" ; this should thus do nothing
        self.assertFalse(PATH4.exists())
        PATH4.write_text("BAD")
        self.assertRaises(ValueError, PATH4.load)
        self.assertRaises(ValueError, PATH4.ask, id=("BAD", "identifier", "format"))
        self.assertRaises(ValueError, PATH4.ask, secret=("BAD", "secret", "format"))
        PATH4.remove()
        PATH4.touch()
        self.assertIsNone(PATH4.load())
        self.assertEqual(PATH4.id, "")
        self.assertEqual(PATH4.secret, "")
        PATH4.remove()
        Path("test_creds").remove()
    
    def test_mirror_path(self):
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
    
    def test_project_path(self):
        self.assertRaises(ValueError, ProjectPath, FILE)
        p = ProjectPath(str(TPATH2), {'README': "#TODO: test", 'folder': {'file1': "test file", 'file2': None}})
        self.assertEqual(p.todo, {str(Path(str(TPATH2)).joinpath("README")) + ':1': "test",
                                  str(Path(str(TPATH2)).joinpath("modules", "test2.py")) + ':Test:7': "test"})
        self.assertEqual(p.fixme, {})
        self.assertIsNotNone(p.search("Test"))
        self.assertRaises(ValueError, p.load)
        p2 = p.archive()
        self.assertFalse(p.exists())
        self.assertTrue(p2.exists())
        self.assertRaises(ValueError, p2.archive)
        p = p2.load()
        self.assertFalse(p2.exists())
        self.assertTrue(p.exists())
    
    def test_python_path(self):
        p = PythonPath(TPATH2, remove_cache=True)
        self.assertEqual(len(p.modules), 2)
        self.assertTrue(any(hasattr(m, "Test") for m in p.modules))
        self.assertEqual(len(list(p.get_classes())), 1)
        p = PythonPath(FILE)
        self.assertFalse(p.loaded)
        self.assertEqual(list(p.get_classes()), [])
        p = PythonPath(MODULE)
        self.assertTrue(p.loaded)
        l = list(p.get_classes())
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].__name__, "Test")
        self.assertFalse(p.has_baseclass(l[0]))
        self.assertTrue(p.has_class(l[0]))
    
    def test_temp_path(self):
        self.assertTrue(TPATH1.exists())
        self.assertEqual(str(TPATH1), gettempdir())
        self.assertTrue(TPATH2.exists())
        self.assertNotEqual(str(TPATH2), gettempdir())
        self.assertEqual(str(TempPath(str(TPATH2))), str(TPATH2))
        self.assertRaises(ValueError, TempPath, Path(".").absolute().root)
        self.assertTrue(TPATH2.tempdir("test").exists())
        self.assertIsNotNone(TPATH2.tempfile())

