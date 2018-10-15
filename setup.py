#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from setuptools import setup


setup(
  name = "tinyscript",
  packages = ["tinyscript"],
  version = "1.0.0",
  license = "AGPLv3",
  description = "A library for quickly building CLI Python-based tools with "
                "basic features in a shortened way",
  author = "Alexandre D\'Hondt",
  author_email = "alexandre.dhondt@gmail.com",
  url = "https://github.com/dhondta/tinyscript",
  download_url = "https://github.com/dhondta/tinyscript/archive/1.0.0.tar.gz",
  keywords = ["CLI", "tool"],
  classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Topic :: Security',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
  python_requires = '>=2.7, >=3.5, <4',
)
