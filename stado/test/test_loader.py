import unittest
import os
import inspect

from stado.stado import Loader, Page, Asset, Content

class TestLoader(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), 'test_loader')


    # Test methods.

    def test_load_module(self):

        path = os.path.join(self.path, 'tree')
        module = Loader(path).load_module('controller.py')

        self.assertTrue(inspect.ismodule(module))
        self.assertEqual('hello world', module.hello)


    def test_load_dir(self):

        path = os.path.join(self.path, 'tree')
        contents = [i for i in Loader(path).load_dir()]

        self.assertEqual(1, len(contents))
        self.assertTrue(contents[0].path.endswith('a.html'))


    def test_load_file(self):

        path = os.path.join(self.path, 'tree')
        page = Loader(path).load_file('a.html')
        self.assertIsInstance(page, Page)


    def test_walk(self):

        path = os.path.join(self.path, 'tree')
        contents = [i for i in Loader(path).walk()]

        self.assertEqual(2, len(contents))
        self.assertTrue(contents[0].path.endswith('a.html'))
        self.assertTrue(contents[1].path.endswith('b.html'))


    # Test file loading.


    def test_load_html_file(self):

        a = Loader(self.path).load_file('a.html')

        self.assertIsInstance(a, Page)
        self.assertEqual(a.template, 'hello world')
        self.assertEqual(a.context, None)


    def test_load_yaml_file(self):

        a = Loader(self.path).load_file('c.yaml')

        self.assertIsInstance(a, Page)
        self.assertEqual(a.template, None)
        self.assertEqual(a.context, {'hello': 'hello world'})


    def test_load_json_file(self):

        a = Loader(self.path).load_file('b.json')

        self.assertIsInstance(a, Page)
        self.assertEqual(a.template, None)
        self.assertEqual(a.context, {'hello': 'hello world'})


    def test_load_asset_file(self):

        a = Loader(self.path).load_file('d.jpg')

        self.assertIsInstance(a, Asset)