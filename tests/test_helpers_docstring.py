#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Dictionary assets' tests.

"""
from tinyscript.helpers.docstring import *

from utils import *


class _Example1(object):
    pass


class _Example2(object):
    """
    This is a test multi-line long 
     description.

    This is a first comment.

    Author: John Doe
             (john.doe@example.com)
    Version: 1.0
    Comments:
    - subcomment 1
    - subcomment 2

    Options:
    - test | str
    - test2 | int

    Something: lorem ipsum
                paragraph

    This is a second comment,
     a multi-line one.

    Options: test3 | list
    """
    pass

_info = {
    'author': "John Doe (john.doe@example.com)",
    'comments': [
        "This is a first comment.",
        ("subcomment 1", "subcomment 2"),
        "This is a second comment, a multi-line one.",
    ],
    'description': "This is a test multi-line long description.",
    'options': [
        ('test', 'str'),
        ('test2', 'int'),
        ('test3', 'list'),
    ],
    'something': "lorem ipsum paragraph",
    'version': "1.0",
}


class TestHelpersDocstring(TestCase):
    def test_parse_docstring(self):
        self.assertEqual(parse_docstring(_Example1), {})
        self.assertEqual(parse_docstring(_Example2.__doc__), _info)
        self.assertEqual(parse_docstring(_Example2), _info)

