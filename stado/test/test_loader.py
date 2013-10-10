import unittest
import os
import inspect

from stado.stado import Loader

class TestLoader(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), 'test_loader')


    def test_load_module(self):

        path = os.path.join(self.path, 'controller.py')
        module = Loader().load_module(path)

        self.assertTrue(inspect.ismodule(module))
        self.assertEqual('hello world', module.hello)


    def test_load_dir(self):

        contents = [i for i in Loader().load_dir(self.path)]

        self.assertEqual(1, len(contents))
        self.assertTrue(contents[0].path.endswith('a.html'))


    def test_walk(self):

        contents = [i for i in Loader().walk(self.path)]

        self.assertEqual(2, len(contents))
        self.assertTrue(contents[0].path.endswith('a.html'))
        self.assertTrue(contents[1].path.endswith('b.html'))