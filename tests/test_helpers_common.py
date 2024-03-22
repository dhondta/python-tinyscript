# -*- coding: UTF-8 -*-
"""Common utility functions' tests.

"""
import lazy_object_proxy
from datetime import datetime
from pytz import timezone
from tinyscript.helpers.common import *

from utils import remove, TestCase


DUMMY_CONST = None


def _init_ospathexists():
    from os.path import exists
    return exists


def _postload(o):
    global DUMMY_CONST
    DUMMY_CONST = "OK"


class TestHelpersCommon(TestCase):
    def test_common_utility_functions(self):
        self.assertRaises(TypeError, range2)
        self.assertRaises(TypeError, range2, ())
        self.assertRaises(TypeError, range2, 1, 2, 3, 4)
        self.assertEqual(list(range2(2)), [0.0, 1.0])
        self.assertEqual(list(range2(0, .5)), [0.0])
        self.assertEqual(len(range2(0, .5)), 1)
        r = range2(0, .5, .1)
        self.assertEqual(repr(r), "range(0.0, 0.5, 0.1)")
        self.assertEqual(list(r), [0.0, 0.1, 0.2, 0.3, 0.4])
        self.assertEqual(r.count(.3), 1)
        self.assertEqual(r.count(.5), 0)
        self.assertEqual(r.index(.2), 2)
        self.assertRaises(ValueError, r.index, 1.1)
        self.assertEqual(human_readable_size(123456), "121KB")
        self.assertRaises(ValueError, human_readable_size, "BAD")
        self.assertRaises(ValueError, human_readable_size, -1)
        self.assertIsNotNone(is_admin())
        self.assertEqual(xor("this is a test", " "), "THIS\x00IS\x00A\x00TEST")
        self.assertEqual(list(strings("this is a \x00 test")), ["this is a ", " test"])
        FILE, CONTENT = ".test_strings", b"this is a \x00 test"
        with open(FILE, 'wb') as f:
            f.write(CONTENT)
        self.assertIsNone(xor_file(FILE, " "))
        self.assertIsNone(xor_file(FILE, " "))
        with open(FILE, 'rb') as f:
            self.assertEqual(f.read(), CONTENT)
        self.assertEqual(list(strings_from_file(FILE)), ["this is a ", " test"])
        remove(FILE)
        tz = timezone("Europe/London")
        self.assertEqual(dateparse("2008"), datetime(2008, datetime.now(tz).month, datetime.now(tz).day))
        def test_func():
            pass
        self.assertTrue(repr(test_func).startswith("<function "))
        @withrepr(lambda f: "<test_function %s at 0x%x" % (f.__name__, id(f)))
        def test_func2():
            pass
        self.assertTrue(repr(test_func2).startswith("<test_function "))
        self.assertEqual(zeropad(5)("ok"), "ok\x00\x00\x00")
        self.assertEqual(zeropad(5)("011"), "01100")
        self.assertEqual(zeropad(5)([0,1,1]), [0,1,1,0,0])
        self.assertEqual(zeropad(5)(["0","1","1"]), ["0","1","1","0","0"])
        self.assertEqual(zeropad(5)(lambda: "ok")(), "ok\x00\x00\x00")
        self.assertEqual(zeropad(5)(lambda: "011")(), "01100")
        self.assertEqual(zeropad(5)([]), ["\x00","\x00","\x00","\x00","\x00"])
        self.assertEqual(zeropad(5, default=0)([]), [0,0,0,0,0])
        self.assertEqual(zeropad(5, default="0")(""), "00000")
    
    def test_lazy_load_functions(self):
        global DUMMY_CONST
        lazy_load_object("exists", _init_ospathexists, postload=_postload)
        self.assertIsNone(DUMMY_CONST)
        self.assertTrue(isinstance(exists, lazy_object_proxy.Proxy))
        self.assertTrue(exists(__file__))
        self.assertTrue(isinstance(exists, type(lambda: None)))
        self.assertIsNotNone(DUMMY_CONST)
        DUMMY_CONST = None
        lazy_load_module("re.sre_parse", alias="sre_parse")
        self.assertTrue(isinstance(sre_parse, lazy_object_proxy.Proxy))
        self.assertRaises(ImportError, getattr, sre_parse, "__class__")  # will raise "'re' is not a package"
        self.assertIsNone(DUMMY_CONST)
        lazy_load_module("re", postload=_postload)
        self.assertTrue(isinstance(re, lazy_object_proxy.Proxy))
        self.assertTrue(isinstance(re.search, type(lambda: None)))
        self.assertIsNotNone(DUMMY_CONST)
        lazy_load_object("dummy_alias", lambda: str)
    
    def test_deprecation(self):
        def test_func(): pass
        deprecate(test_func, "new_test_func")
        self.assertIsNone(test_func())
        deprecate("old.module", "new.module")

