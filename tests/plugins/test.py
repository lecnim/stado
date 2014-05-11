import unittest

from tests.plugins.example_plugin import ExamplePlugin, Class, function
from tests.plugins.example_apply import apply
from stado import plugins


class TestPlugins(unittest.TestCase):
    """
    Plugins loading system
    """

    def test_default_import(self):
        """should load default plugin class (written in CamelCase)"""

        p = plugins.load_plugin('example_plugin', package='tests.plugins')
        self.assertEqual(ExamplePlugin, p)

    def test_global_apply(self):
        """should use global apply() instead of default plugin class"""

        p = plugins.load_plugin('example_apply', package='tests.plugins')
        self.assertEqual(apply, p)

    def test_syntax(self):
        """accept plugin name with dash: foo-bar"""

        p = plugins.load_plugin('example-plugin', package='tests.plugins')
        self.assertEqual(ExamplePlugin, p)

    def test_import_using_dot(self):
        """should load other objects in plugin module using dot: foo.bar"""

        # Importing class.
        p = plugins.load_plugin('example_plugin.Class', package='tests.plugins')
        self.assertEqual(Class, p)

        # Importing function.
        p = plugins.load_plugin('example_plugin.function',
                                package='tests.plugins')
        self.assertEqual(function, p)