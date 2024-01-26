# -*- coding: UTF-8 -*-
"""Preimports random assets' tests.

"""
from collections import Counter
from math import log
from tinyscript.preimports import random

from utils import *


class TestPreimportsRandom(TestCase):
    def test_utility_functions(self):
        self.assertEqual(random.choice([1, 2, 3], [2, 3]), 1)
        self.assertRaises(IndexError, random.choice, [])
        self.assertIsNone(random.choice([], error=False))
        self.assertIsNotNone(random.randstr())
        self.assertEqual(random.randstr(0), "")
        self.assertEqual(len(random.randstr()), 8)
        self.assertEqual(len(random.randstr(20)), 20)
        self.assertNotIn("e", random.randstr(alphabet="abcd"))
        self.assertRaises(ValueError, random.randstr, -1)
        self.assertRaises(ValueError, random.randstr, 8, "")
        self.assertTrue(isinstance(random.randstr(16, b"\x00\x01\x02"), bytes))
        for n, na in zip([8, 16, 64], [3, 4, 5]):
            for bs in [0, 16, 256]:
                for i in range(512):
                    self.assertLess(max(Counter(random.randstr(n, "".join(chr(i) for i in range(na)), True, bs))\
                                        .values()), n/(na-1) if (bs or n) > (na-1)/(1-(na-1)/na) else n/(na-2))
    
    def test_random_lfsr(self):
        l = random.LFSR(target="0123456789abcdef")
        self.assertEqual(l.next_block("hex", update=False), "9617f3cf")
        self.assertEqual(l.next_block("hex"), "9617f3cf")
        self.assertEqual(l.next_block("hex"), "91f53906")
        self.assertTrue(l.next_block("str"))
        self.assertTrue(l.next_block("bin"))
        self.assertRaises(ValueError, random.LFSR)
        self.assertRaises(ValueError, random.LFSR, target=1234)
        self.assertRaises(ValueError, random.LFSR, "NO_NBITS_DEFINED")
        self.assertRaises(ValueError, random.LFSR, 1234, "BAD_TAPS", 32)
        self.assertRaises(ValueError, random.LFSR, "TOO_BIG_SEED", (1, 2, 3), 32)
        self.assertRaises(ValueError, random.LFSR, 0, (1, 2, 3), 32)
        self.assertRaises(ValueError, random.LFSR, ["B", "A", "D", "S", "E", "E", "D"], (1, 2, 3), 32)
        self.assertRaises(ValueError, l.next_block, "BAD_OUTPUT_FORMAT")
        self.assertRaises(ValueError, l.test, "abcd")
        self.assertTrue(l.next_block("str"))
        self.assertTrue(l.next_block("bin"))
        random.LFSR("abcdef", (1, 3, 5, 7), 32)
    
    def test_random_geffe(self):
        g = random.Geffe("1234567890ab")
        self.assertEqual(g.next_block("hex", update=False), "f59f02da")
        self.assertEqual(g.next_block("hex"), "f59f02da")
        self.assertEqual(g.next_block("hex"), "56ef5ba8")
        self.assertTrue(g.next_block("str"))
        self.assertTrue(g.next_block("bin"))
        self.assertTrue(g.next_block("hex"))
        g = random.Geffe("".join(map(str, [random.randint(0, 1) for _ in range(96)])))
        g = random.Geffe(["a", "b", "c"])
        self.assertTrue(g.next_block("hex"))
        g = random.Geffe([random.randint(0, 1) for _ in range(96)])
        self.assertRaises(ValueError, random.Geffe, key="bad_key_of_length_20")
        self.assertRaises(ValueError, random.Geffe, seeds="BAD_SEEDS")
        self.assertRaises(ValueError, g.next_block, "BAD_OUTPUT_FORMAT")

