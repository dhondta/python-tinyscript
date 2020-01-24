#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Preimports code assets' tests.

"""
from tinyscript import b, ensure_str, ts, PYTHON3
from tinyscript.preimports import codecs

from utils import *


class TestPreimportsCodecs(TestCase):
    def setUp(self):
        global STR
        STR = "this is a test"
    
    def test_add_codec(self):
        f = lambda: None
        self.assertRaises(ValueError, codecs.add_codec, "test")
        self.assertRaises(ValueError, codecs.add_codec, "test", "BAD")
        self.assertRaises(ValueError, codecs.add_codec, "test", f, "BAD")
    
    def test_codec_leetspeak(self):
        LTS = "7H15 15 4 7357"
        TFILE = "test-codec-leetspeak.txt"
        self.assertTrue(ts.is_str(codecs.encode(STR, "leet")))
        self.assertEqual(codecs.encode(STR, "leet").upper(), LTS)
        self.assertEqual(codecs.encode(STR, "1337").upper(), LTS)
        self.assertEqual(codecs.encode(STR, "leetspeak").upper(), LTS)
        self.assertEqual(codecs.encode(STR, "13375p34k").upper(), LTS)
        self.assertTrue(not PYTHON3 or
                        ts.is_bytes(codecs.encode(b(LTS), "leet")))
        if PYTHON3:
            with open(TFILE, 'w', encoding="leet") as f:
                f.write(STR)
            with open(TFILE, encoding="leet") as f:
                s = f.read().strip()
            self.assertEqual(STR.upper(), s.upper())
        with codecs.open(TFILE, 'w', encoding="leet") as f:
            f.write(b(STR))
        with codecs.open(TFILE, encoding="leet") as f:
            s = f.read().strip()
        self.assertEqual(STR.upper(), ensure_str(s.upper()))
        remove(TFILE)
    
    def test_codec_markdown(self):
        HTM = "<h1>Test title</h1>\n\n<p>Test paragraph</p>\n"
        MD  = "# Test title\n\nTest paragraph"
        TFILE = "test-codec-markdown.html"
        self.assertTrue(ts.is_str(codecs.encode(MD, "markdown")))
        self.assertTrue(not PYTHON3 or
                        ts.is_bytes(codecs.encode(b(MD), "markdown")))
        self.assertEqual(codecs.encode(MD, "markdown"), HTM)
        self.assertRaises(NotImplementedError, codecs.decode, MD, "markdown")
        if PYTHON3:
            with open(TFILE, 'w', encoding="markdown") as f:
                f.write(MD)
            with open(TFILE) as f:
                s = f.read()
            self.assertEqual(HTM, s)
        with codecs.open(TFILE, 'w', encoding="markdown") as f:
            f.write(b(MD))
        with codecs.open(TFILE) as f:
            s = f.read()
        self.assertEqual(HTM, ensure_str(s))
        remove(TFILE)
    
    def test_codec_morse(self):
        STRB = STR + "#"
        MRS  = "- .... .. ... / .. ... / .- / - . ... -"
        MRSB = MRS + " .........."
        TFILE = "test-codec-morse.txt"
        self.assertTrue(ts.is_str(codecs.encode(STR, "morse")))
        self.assertEqual(codecs.encode(STR, "morse"), MRS)
        self.assertRaises(ValueError, codecs.encode, STRB, "morse")
        self.assertIsNotNone(codecs.encode(STRB, "morse", "replace"))
        self.assertIsNotNone(codecs.encode(STRB, "morse", "ignore"))
        self.assertRaises(ValueError, codecs.decode, MRSB, "morse")
        self.assertIsNotNone(codecs.decode(MRSB, "morse", "replace"))
        self.assertIsNotNone(codecs.decode(MRSB, "morse", "ignore"))
        self.assertIsNotNone(codecs.encode(STR, "morse", "BAD_ERRORS"))
        self.assertRaises(ValueError, codecs.encode, "#", "morse", "BAD_ERRORS")
        self.assertRaises(ValueError, codecs.decode, "#", "morse", "BAD_ERRORS")
        self.assertTrue(not PYTHON3 or
                        ts.is_bytes(codecs.encode(b(STR), "morse")))
        if PYTHON3:
            with open(TFILE, 'w', encoding="morse") as f:
                f.write(STR)
            with open(TFILE, encoding="morse") as f:
                s = f.read().strip()
            self.assertEqual(STR, s)
        with codecs.open(TFILE, 'w', encoding="morse") as f:
            f.write(b(STR))
        with codecs.open(TFILE, encoding="morse") as f:
            s = f.read().strip()
        self.assertEqual(STR, ensure_str(s))
        remove(TFILE)
    
    def test_codec_rotn(self):
        RT1 = "uijt jt b uftu"
        RT3 = "wklv lv d whvw"
        TFILE = "test-codec-rotn.txt"
        self.assertTrue(ts.is_str(codecs.encode(STR, "rot12")))
        self.assertEqual(codecs.encode(STR, "rot1"), RT1)
        self.assertEqual(codecs.encode(STR, "rot-1"), RT1)
        self.assertEqual(codecs.encode(STR, "rot_1"), RT1)
        self.assertEqual(codecs.encode(STR, "ROT1"), RT1)
        self.assertEqual(codecs.encode(STR, "ROT-1"), RT1)
        self.assertEqual(codecs.encode(STR, "ROT_1"), RT1)
        self.assertEqual(codecs.decode(RT1, "rot1"), STR)
        self.assertRaises(LookupError, codecs.decode, STR, "rot0")
        self.assertRaises(LookupError, codecs.decode, STR, "rot--10")
        self.assertRaises(LookupError, codecs.decode, STR, "rot100")
        s = STR
        for i in range(1, 26):
            old = s
            s = codecs.encode(s, "rot1")
            self.assertEqual(codecs.decode(s, "rot1"), old)
        self.assertTrue(not PYTHON3 or
                        ts.is_bytes(codecs.encode(b(STR), "rot1")))
        if PYTHON3:
            with open(TFILE, 'w', encoding="rot-3") as f:
                f.write(STR)
            with open(TFILE) as f:
                r = f.read().strip()
            self.assertEqual(RT3, r)
            with open(TFILE, encoding="rot-3") as f:
                s = f.read().strip()
            self.assertEqual(STR, s)
        with codecs.open(TFILE, 'w', encoding="rot-3") as f:
            f.write(b(STR))
        with open(TFILE) as f:
            r = f.read().strip()
        self.assertEqual(RT3, r)
        with codecs.open(TFILE, encoding="rot-3") as f:
            s = f.read().strip()
        self.assertEqual(STR, ensure_str(s))
        remove(TFILE)
    
    def test_codec_xorn(self):
        XR3 = "wkjp#jp#b#wfpw"
        XR6 = "rnou&ou&g&rcur"
        TFILE = "test-codec-xorn.txt"
        self.assertTrue(ts.is_str(codecs.encode(STR, "xor200")))
        self.assertEqual(codecs.encode(STR, "xor3"), XR3)
        self.assertEqual(codecs.encode(STR, "xor-3"), XR3)
        self.assertEqual(codecs.encode(STR, "xor_3"), XR3)
        self.assertEqual(codecs.encode(STR, "XOR6"), XR6)
        self.assertEqual(codecs.encode(STR, "XOR-6"), XR6)
        self.assertEqual(codecs.encode(STR, "XOR_6"), XR6)
        self.assertEqual(codecs.decode(XR3, "xor3"), STR)
        self.assertRaises(LookupError, codecs.decode, STR, "xor0")
        self.assertRaises(LookupError, codecs.decode, STR, "xor--10")
        self.assertRaises(LookupError, codecs.decode, STR, "xor256")
        self.assertRaises(LookupError, codecs.decode, STR, "xor300")
        s = STR
        for i in range(1, 256):
            old = s
            s = codecs.encode(s, "xor1")
            self.assertEqual(codecs.decode(s, "xor1"), old)
        self.assertTrue(not PYTHON3 or
                        ts.is_bytes(codecs.encode(b(STR), "xor1")))
        if PYTHON3:
            with open(TFILE, 'w', encoding="xor-3") as f:
                f.write(STR)
            with open(TFILE) as f:
                r = f.read().strip()
            self.assertEqual(XR3, r)
            with open(TFILE, encoding="xor-3") as f:
                s = f.read().strip()
            self.assertEqual(STR, s)
        with codecs.open(TFILE, 'w', encoding="xor-3") as f:
            f.write(b(STR))
        with open(TFILE) as f:
            r = f.read().strip()
        self.assertEqual(XR3, r)
        with codecs.open(TFILE, encoding="xor-3") as f:
            s = f.read().strip()
        self.assertEqual(STR, ensure_str(s))
        remove(TFILE)
