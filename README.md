<p align="center"><img src="https://github.com/dhondta/python-tinyscript/raw/main/docs/pages/img/logo.png"></p>
<h1 align="center">TinyScript <a href="https://twitter.com/intent/tweet?text=TinyScript%20-%20Devkit%20for%20quickly%20building%20CLI%20tools%20with%20Python.%0D%0APython%20library%20with%20many%20features%20for%20writing%20short,%20simple%20and%20nice-looking%20CLI%20tools.%0D%0Ahttps%3a%2f%2fgithub%2ecom%2fdhondta%2fpython-tinyscript%0D%0A&hashtags=python,programming,devkit,console,cli,tools,ctftools"><img src="https://img.shields.io/badge/Tweet--lightgrey?logo=twitter&style=social" alt="Tweet" height="20"/></a></h1>
<h3 align="center">Make a CLI tool with very few lines of code.</h3>

[![PyPi](https://img.shields.io/pypi/v/tinyscript.svg)](https://pypi.python.org/pypi/tinyscript/)
[![Read The Docs](https://readthedocs.org/projects/python-tinyscript/badge/?version=latest)](https://python-tinyscript.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://github.com/dhondta/python-tinyscript/actions/workflows/python-package.yml/badge.svg)](https://github.com/dhondta/python-tinyscript/actions/workflows/python-package.yml)
[![Coverage Status](https://raw.githubusercontent.com/dhondta/python-tinyscript/main/docs/coverage.svg)](#)
[![Python Versions](https://img.shields.io/pypi/pyversions/tinyscript.svg)](https://pypi.python.org/pypi/tinyscript/)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/python-tinyscript/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/python-tinyscript?targetFile=requirements.txt)
[![License](https://img.shields.io/pypi/l/tinyscript.svg)](https://pypi.python.org/pypi/tinyscript/)

This library is aimed to provide useful features and helpers in order to shorten the number of required lines of code for writing simple and nice-looking command-line interface tools. It is based on `argparse` and is considered a **development kit**, on the contrary of popular **frameworks** like [`cement`](https://builtoncement.com/), [`click`](https://click.palletsprojects.com) or [`docopt`](http://docopt.org), as it is not aimed to reinvent the wheel in yet another paradigm.

```sh
pip install tinyscript
```

## :bulb: Philosophy

This library is built with the DRY (*Don't Repeat Yourself*) and KISS (*Keep It Stupid Simple*) philosophies in mind ; the whole machinery of Tinyscript holds in its **star import** (`from tinyscript import *`) and its **initialization** (with the `initialize` function).

It is aimed to shorten required code by setting a few things while loaded:
- a [*proxy* parser](https://python-tinyscript.readthedocs.io/en/latest/internals.html#proxy-parser) (coming from the star import) collects arguments definitions and formats help at initialization, preventing from rewriting the whole bunch of code needed to declare an [`ArgumentParser`](https://docs.python.org/3/library/argparse.html#example) (and define its epilog, and so forth)
- a [main (colored) logger](https://python-tinyscript.readthedocs.io/en/latest/internals.html#pre-configured-colored-logger) is preconfigured and can be tuned through two constants so that we don't care for writing a bunch of code needed to configure logging
- [preimports](https://python-tinyscript.readthedocs.io/en/latest/internals.html#pre-imports) (while a bit anti-Pythonic, we confess) of common libraries also reduces the quantity of code required
- among these, some [modules are enhanced](https://python-tinyscript.readthedocs.io/en/latest/enhancements.html) with new functions and classes that are not natively foreseen

Leveraging this allows to create very short scripts with **only the real code that matters**, reducing the code to be rewritten to create efficient, nice-looking and sophisticated CLI tools.

Note that, while star imports should be avoided according to Python's style guide (see [PEP8](https://pep8.org/#imports)), it is deliberately extensively used and covering a huge scope in order to shorten code length. This "anti-pattern" pays off after creating a few tools, when we can realize it shortens parts of the code that are often repeated from a tool to another (e.g. for shaping tool's help message).

## :sunglasses: Usage

It is designed to be as simple and straightforward to use as possible. In order to learn and use it, you only need your browser (for consulting the documentation), a text editor and a good Python Interpreter (e.g. [IDLE](https://docs.python.org/3/library/idle.html)) for using auto-completion or an IDE like [PyCharm](https://www.jetbrains.com/pycharm/) to get helpers suggested.

The point is that you will use:
- [features](https://python-tinyscript.readthedocs.io/en/latest/utility.html), enabled by setting flags in the "master" function called `ìnitialize`
- [helpers](https://python-tinyscript.readthedocs.io/en/latest/helpers.html), grouped under the "master" submodule called `ts`
- [reporting](https://python-tinyscript.readthedocs.io/en/latest/reporting.html) objects from the global scope

Please see the [example tools](#example-tools) herebelow for examples of usage of features, helpers and reporting.

## :fast_forward: Quick Start

### Create from template

<p align="center"><img src="https://raw.githubusercontent.com/dhondta/python-tinyscript/main/docs/pages/demos/create.svg"></p>

### Edit source

<p align="center"><img src="https://raw.githubusercontent.com/dhondta/python-tinyscript/main/docs/pages/demos/edit.svg"></p>

### Run your tool

<p align="center"><img src="https://raw.githubusercontent.com/dhondta/python-tinyscript/main/docs/pages/demos/run.svg"></p>

## :mag: Example tools

### Security

- [AppMemDumper](https://github.com/dhondta/AppmemDumper) (Windows forensics)
- [Bots Scheduler](https://github.com/dhondta/bots-scheduler) (Web security services job scheduler)
- [DroneSploit](https://github.com/dhondta/dronesploit) (startup script)
- [Evil Pickle Creation Tool](https://gist.github.com/dhondta/0224d42a6f9dde00247ff8646f4e89aa) (Python evil pickle generation tool)
- [Malicious Macro Tester](https://github.com/dhondta/malicious-macro-tester) (malicious VB macro detection)
- [Paddinganograph](https://gist.github.com/dhondta/90a07d9d106775b0cd29bb51ffe15954) (base32/64 padding-based steganography)
- [PDF Passwords Bruteforcer](https://gist.github.com/dhondta/efe84a92e4dfae3b6c14932c73ab2577) (bruteforce tool)
- [Solitaire Cipher](https://gist.github.com/dhondta/1858f406fc55e5e5d440ff26432ad0a4) (encryption)
- [StegoLSB](https://gist.github.com/dhondta/d2151c82dcd9a610a7380df1c6a0272c) (Least Significant Bit)
- [StegoPIT](https://gist.github.com/dhondta/30abb35bb8ee86109d17437b11a1477a) (Pixel Indicator Technique)
- [StegoPVD](https://gist.github.com/dhondta/feaf4f5fb3ed8d1eb7515abe8cde4880) (Pixel Value Differencing)
- [STIX Report Generator](https://gist.github.com/dhondta/ca5fb748957b1ec6f13418ac41c94d5b)
- [WLF (Word List Filter)](https://gist.github.com/dhondta/82a7919f8aafc1393c37c2d0f06b77e8)

### Utils

- [Audio Assembler](https://gist.github.com/dhondta/8b3c7d95b056cae3505df853a098fc4f)
- [Documentation Text Masker](https://gist.github.com/dhondta/5cae9533240471eac155bd51593af2e0)
- [Email Origin](https://gist.github.com/dhondta/9a8027062ff770b2aa5d8422ddd78b57)
- [Loose Comparison Input Generator](https://gist.github.com/dhondta/8937374f087f708c608bcacac431969f) (PHP Type Juggling)
- [PDF Preview Generator](https://gist.github.com/dhondta/f57dfde304905644ca5c43e48c249125)
- [Recursive Compression](https://github.com/dhondta/recursive-compression)
- [WebGrep](https://github.com/dhondta/webgrep) (Web text search)
- [Zotero CLI](https://github.com/dhondta/zotero-cli)


## :clap:  Supporters

[![Stargazers repo roster for @dhondta/python-tinyscript](https://reporoster.com/stars/dark/dhondta/python-tinyscript)](https://github.com/dhondta/python-tinyscript/stargazers)

[![Forkers repo roster for @dhondta/python-tinyscript](https://reporoster.com/forks/dark/dhondta/python-tinyscript)](https://github.com/dhondta/python-tinyscript/network/members)

<p align="center"><a href="#"><img src="https://img.shields.io/badge/Back%20to%20top--lightgrey?style=social" alt="Back to top" height="20"/></a></p>
