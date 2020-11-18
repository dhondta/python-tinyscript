#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Progress management module assets' tests.

"""
from tinyscript.features.progress import set_progress_items

from utils import *


args.progress = True
set_progress_items(globals())


class TestProgress(TestCase):    
    def test_progress_setup(self):
        g = globals().keys()
        self.assertTrue(args.progress)
        self.assertIn("progress_manager", g)

    def test_progress_manager(self):
        p = progress_manager
        temp_stdout(self)
        p.start(total=10)
        self.assertIsNotNone(p._tqdm)
        p.update(5)
        p.update(10)
        p.stop()
        self.assertIsNone(p._tqdm)

    def test_progress_bar(self):
        for i in progressbar(10):
            continue
        for i in progressbar([1, 2, 3]):
            continue

