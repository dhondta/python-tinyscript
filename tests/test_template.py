#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Template module assets' tests.

"""
from tinyscript.template import new, IMPORTS, SHEBANG, TOOL_METADATA

from utils import *


class TestTemplate(TestCase):
    def _get(self, template, target=None, name=None):
        new(template, target, name)
        name = "{}.py".format(name or template)
        imp = "" if target is None else "from {} import {}\n" \
                                        .format(*target.split('.'))
        with open(name) as f:
            content = f.read()
        remove(name)
        return name, imp, content
    
    def test_script_generation(self):
        name, imp, content = self._get("script")
        self.assertEqual(name, "script.py")
        self.assertEqual(imp, "")
        self.assertIn(IMPORTS.format(target=imp), content)
        self.assertIn(SHEBANG, content)
    
    def test_tool_generation(self):
        name, imp, content = self._get("tool", name="test")
        self.assertEqual(name, "test.py")
        self.assertEqual(imp, "")
        self.assertIn(SHEBANG, content)
        self.assertIn(TOOL_METADATA, content)
    
    def test_pybots_script_generation(self):
        name, imp, content = self._get("script", "pybots.HTTPBot")
        self.assertEqual(name, "script.py")
        self.assertEqual(imp, "from pybots import HTTPBot\n")
        self.assertIn(SHEBANG, content)
        self.assertIn(imp, content)
        self.assertIn(IMPORTS.format(target=imp), content)
        self.assertRaises(ValueError, new, "test")
        self.assertRaises(ValueError, new, "script", "bad.library")
        self.assertRaises(ValueError, new, "script", name="bad/name")
