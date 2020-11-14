#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Dictionary assets' tests.

"""
from tinyscript.helpers.dictionaries import *

from utils import *


class TestHelpersDictionaries(TestCase):
    def test_flatten_dictionary(self):
        d = {'k': "test", 'k2': {'sk': "test2"}}
        self.assertEqual(flatten_dict(d), {'k': "test", 'k2/sk': "test2"})
    
    def test_merge_dictionaries(self):
        d1, d2 = {'k': "test1"}, {'k': "test2"}
        self.assertEqual(merge_dict(d1, d2), d2)
        self.assertEqual(merge_dict(d1, d2, update=False), d1)
        d2['k2'] = "test3"
        self.assertEqual(merge_dict(d1, d2), d2)
        self.assertEqual(merge_dict(d1, d2, update=False), d1)
        del d1['k2'], d2['k2']
        d1['k'], d2['k'] = {'d': "test1"}, {'d': "test2"}
        self.assertEqual(merge_dict(d1, d2), d2)
        d1['k'], d2['k'] = ("test1",), ("test2",)
        self.assertEqual(merge_dict(d1, d2)['k'], ("test1", "test2"))
        d1['k'], d2['k'] = {"test1"}, {"test2"}
        self.assertEqual(merge_dict(d1, d2)['k'], {"test1", "test2"})
        d3 = merge_dict(d1, d2)
        self.assertEqual(id(d1), id(d3))
        d3 = merge_dict(d1, d2, new=True)
        self.assertNotEqual(id(d1), id(d3))
    
    def test_class_registry(self):
        d = ClassRegistry()
        class Base: pass
        class Sub1: pass
        class Sub2: pass
        class Sub3: pass
        Sub3.__name__ = "Sub2"
        self.assertIsNone(d[None])
        self.assertRaises(KeyError, d.__getitem__, "base")
        d[Base] = Sub1
        self.assertEqual(Sub1, d['Base', 'Sub1'])
        self.assertEqual(Sub1, d[Base, Sub1])
        self.assertEqual([Sub1], list(d))
        d[Base] = Sub2
        d[Base] = Sub3
        self.assertEqual([Sub2, Sub3], d['base', 'sub2'])
        self.assertIsNone(d.__delitem__(("base", "sub1")))
        self.assertRaises(ValueError, d.__delitem__, ("base", "sub1"))
        self.assertIsNone(d.__delitem__("base"))
        self.assertRaises(KeyError, d.__delitem__, "base")
        d[Base] = Sub1
        self.assertEqual(Sub1, d[None, 'sub1'])
        self.assertIsNone(d.__delitem__((None, Sub1)))
    
    def test_expiring_dictionary(self):
        d = ExpiringDict(max_age=.1)
        d['test'] = "test"
        self.assertEqual(d['test'], "test")
        self.assertEqual(d.get('test'), "test")
        sleep(.2)
        self.assertIsNone(d.get('test'))
        self.assertRaises(ValueError, d.__getitem__, "test")
        d = ExpiringDict({'test': "test"}, max_age=.2, test2="test")
        self.assertEqual(d['test'], "test")
        self.assertEqual(d['test2'], "test")
        sleep(.2)
        self.assertRaises(ValueError, d.__getitem__, "test")
        self.assertRaises(ValueError, d.__getitem__, "test2")
        d = ExpiringDict({'test': "test"}, max_age=.2, test2="test")
        self.assertIsNone(d.lock())
        sleep(.2)
        self.assertEqual(d['test'], "test")
        self.assertEqual(d['test2'], "test")
        self.assertIsNone(d.unlock())
        self.assertRaises(ValueError, d.__getitem__, "test")
        self.assertRaises(ValueError, d.__getitem__, "test2")
        d['test'] = "test"
        d['test'] = "test"
        sleep(.2)
        d['test'] = "test"
        self.assertEqual(str(d), "{'test': 'test'}")
        d = ExpiringDict()
        d['test2'] = "test"
        d['test1'] = "test"
        self.assertEqual([k for k in d], ["test2", "test1"])
        self.assertEqual([k for k, _ in d.items()], ["test2", "test1"])
        d = ExpiringDict(sort_by_time=False)
        d['test2'] = "test"
        d['test1'] = "test"
        self.assertEqual([k for k in d], ["test1", "test2"])
        self.assertEqual([k for k, _ in d.items()], ["test1", "test2"])
    
    def test_path_based_dictionary(self):
        d = PathBasedDict()
        d['path/to/test'] = "test"
        self.assertEqual(d, {'path': {'to': {'test': 'test'}}})
        self.assertRaises(ValueError, d.__setitem__, 'path/to/test/2', "test2")
        self.assertRaises(KeyError, d.__delitem__, 'path/to/bad')
        del d['path/to/test']
        self.assertRaises(KeyError, d.__delitem__, 'does/not/exist')
        self.assertEqual(d, {})
        d['path', 'to', 'test'] = "test"
        self.assertEqual(d, {'path': {'to': {'test': 'test'}}})
        d['path', 'to', 'test'] = PathBasedDict()
        d['path', 'to', 'test', 'test2'] = "test"
        self.assertEqual(d['path', 'to', 'test', 'test2'], "test")
        d['path', 'to', 'test', 'test3'] = "test"
        self.assertEqual(d.count(), 2)

