import unittest

from tests.plugins.example_plugin import ExamplePlugin, Class, function, example
from tests.plugins.example_apply import apply
from stado import plugins


class Plugin(plugins.Plugin):

    i = 0

    def install(self, site):
        self.i += 1


class TestPluginManager(unittest.TestCase):
    """
    Plugin manager
    """

    def setUp(self):
        self.manager = plugins.PluginsManager(site=None)

    # locals / globals

    # TODO:


    # plugin instance

    def test_install_instance(self):
        """should install plugin instance: Plugin()"""

        plugin = Plugin()
        x = self.manager.get(plugin)
        self.assertEqual(1, plugin.i)
        self.assertEqual(x, plugin)

    def test_skip_install_instance(self):
        """should skip installing plugin instance if it already installed"""

        plugin = Plugin()
        self.manager.get(plugin)
        x = self.manager.get(plugin)
        self.assertEqual(1, plugin.i)
        self.assertEqual(x, plugin)

    # plugin class

    def test_install_class(self):
        """should install plugin class: Plugin"""

        plugin = self.manager.get(Plugin)
        self.assertNotEqual(Plugin, plugin)
        self.assertEqual(1, plugin.i)

    def test_skip_install_class(self):
        """should skip installing plugin class if it already installed"""

        x = self.manager.get(Plugin)
        y = self.manager.get(Plugin)
        self.assertEqual(x, y)
        self.assertEqual(1, x.i)

    # plugin from string - class

    def test_install_class_from_string(self):
        """should import class from string and install it"""

        self.manager.package = 'tests.plugins'

        plugin = self.manager.get('example_plugin')
        self.assertIsInstance(plugin, ExamplePlugin)
        self.assertEqual(1, plugin.i)

    def test_skip_install_class_from_string(self):
        """should skip importing class from string if it already installed"""

        self.manager.package = 'tests.plugins'

        x = self.manager.get('example_plugin')
        y = self.manager.get('example_plugin')
        self.assertEqual(x, y)
        self.assertEqual(1, x.i)

    def test_skip_import_class_from_string(self):
        """should skip importing class from string if already imported"""

        x = self.manager.get(ExamplePlugin)
        self.assertEqual(1, x.i)

        # ExamplePlugin is already imported and installed!
        self.manager.package = 'tests.plugins'
        y = self.manager.get('example_plugin')
        self.assertEqual(x, y)
        self.assertEqual(1, y.i)

    # plugin from string - function

    def test_install_function_from_string(self):
        """should import function from string and install it"""

        self.manager.package = 'tests.plugins'

        plugin = self.manager.get('example_plugin.function')
        self.assertEqual(function, plugin)

    # plugin from string - instance

    def test_install_instance_from_string(self):
        """should import instance from string and install it"""

        self.manager.package = 'tests.plugins'

        example.i = 0
        plugin = self.manager.get('example_plugin.example')
        self.assertIsInstance(plugin, ExamplePlugin)
        self.assertEqual(1, plugin.i)

    def test_skip_install_instance_from_string(self):
        """should skip importing instance from string if it already installed"""

        self.manager.package = 'tests.plugins'

        example.i = 0
        x = self.manager.get('example_plugin.example')
        y = self.manager.get('example_plugin.example')
        self.assertEqual(x, y)
        self.assertEqual(1, x.i)

    def test_skip_import_instance_from_string(self):
        """should skip importing instance from string if already imported"""

        example.i = 0
        x = self.manager.get(example)
        self.assertEqual(1, x.i)

        # example plugin is already imported and installed!
        self.manager.package = 'tests.plugins'
        y = self.manager.get('example_plugin.example')
        self.assertEqual(x, y)
        self.assertEqual(1, y.i)


class TestPluginLoading(unittest.TestCase):
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