# -*- coding: UTF-8 -*-
"""Preimports string assets' tests.

"""
from tinyscript.preimports import json

from utils import *


FNAME = ".test.json"
TEST_JSON = """
  # test long comment 1
  #  with another line
{
  "test": ["a", "b", "c"],
  "other": 1 # test comment 2
}
"""


class TestPreimportsJson(TestCase):
    @classmethod
    def tearDownClass(cls):
        remove(FNAME)
    
    def test_commented_json_dumping(self):
        with open(FNAME, 'wt') as f:
            f.write(TEST_JSON)
        with open(FNAME) as f:
            d = json.loadc(f)
        d['another'] = True
        with open(FNAME, 'wb') as f:
            json.dumpc(d, f)
        with open(FNAME) as f:
            content = f.read()
        self.assertIn("  # test long comment 1", content)
        self.assertIn("  #  with another line", content)
        self.assertIn(" # test comment 2", content)
    
    def test_commented_json_loading(self):
        with open(FNAME, 'wt') as f:
            f.write(TEST_JSON)
        with open(FNAME) as f:
            self.assertIsNotNone(json.loadc(f))
        with open(FNAME, 'wb') as f:
            f.write(TEST_JSON.encode())
        with open(FNAME, 'rb') as f:
            d = json.loadc(f)
        self.assertIn('test', d)
        self.assertIn('other', d)

