import unittest
import os
import inspect

from stado.stado import Loader

class TestLoader(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), 'test_loader')


    def test_load_content(self):



        contents = [i for i in Loader(self.path).load()]

        self.assertIn('.\\a.html', contents)
        self.assertIn('.\\a\\b.html', contents)
        self.assertNotIn('.\\a', contents)
        self.assertNotIn('.\\controller.py', contents)

    def test_load_controller(self):

        module = Loader(self.path).load_controller()

        self.assertTrue(inspect.ismodule(module))
        self.assertEqual('hello world', module.hello)