import importlib
import sys
import inspect

from .. import log
from .. import utils
from .. import IS_ZIP_PACKAGE, PATH


class Plugin:
    def __repr__(self):
        return "{}".format(self.__class__.__name__)

    def install(self, site):
        pass

    def apply(self, site, item):
        pass

    # Locals

    def set_local(self, site, name, value):
        site.plugins.locals[self][name] = value

    def get_local(self, site, name):
        return site.plugins.locals[self].get(name)

    def get_locals(self, site):
        return site.plugins.locals[self]


class PluginsManager:
    """Plugins manager. It imports, installs and keeps plugins in one place."""

    def __init__(self, site):

        self.site = site

        # Plugins locals variables. Each plugin instance has it own.
        self.locals = {}
        # Here are plugins instances that are auto created because of
        # string usage in site.apply() or site.build() methods. For example:
        # site.build('*.html', 'html') => it will creates html plugin and stores
        # it in self.links['html']
        self.links = {}
        # List of installed plugins.
        self.plugins = []
        # Package used during installing plugin from string.
        self.package = 'stado.plugins'

    def __contains__(self, item):
        """Checks if plugin is installed."""
        return True if item in self.plugins or item in self.links else False

    # Getting plugins.

    def get(self, plugin):
        """Returns plugin instance. Also installs plugin if it is not installed
        already. If plugin is string it will try to import it.

        Args:
            plugin: Accepts string, class, plugin instance, function."""

        # Plugin is not installed! Install it first!
        if not plugin in self:
            self.install(plugin)

        return self.links.get(plugin, plugin)

    # Installing plugins.

    def install(self, plugin):
        """Depends on plugin type:
        class: Creates plugin instance from class, adds it to plugins list and
            creates link to it using class.
        str: Import plugin object from module and adds it to plugins and
            creates link to it using string.
        plugin instance: Add to plugins.
        """

        if inspect.isclass(plugin):
            return self._install_class(plugin)

        elif isinstance(plugin, str):
            return self._install_string(plugin)

        else:
            return self._install_object(plugin)

    def _install_object(self, plugin):
        """Installs plugin instance, creates global and local variables for
         plugin. Returns plugin instance."""

        log.debug("Installing plugin (object): " + str(plugin))

        if plugin in self.plugins:
            raise AttributeError('Plugin already installed')

        self.plugins.append(plugin)
        variables = plugin.install(self.site)
        self.locals[plugin] = {} if variables is None else variables

        return plugin

    def _install_class(self, class_):
        """Creates link to plugin instance created from plugin class.
        Returns plugin instance."""

        log.debug("Installing plugin (class): " + str(class_))

        plugin = class_()
        self.links[class_] = plugin
        return self._install_object(plugin)

    def _install_string(self, name):
        """Imports plugin and install it depending on plugin type.

        Args:
            name (str): For example 'foo' will import 'stado.plugins.foo'
        """

        log.debug("Installing plugin (string): " + name)

        plugin = load_plugin(name, package=self.package)

        # Plugin is already installed!
        if plugin in self:
            self.links[name] = self.get(plugin)
        else:
            # Check if plugin is method or function.
            # Do no install it - just create link!
            if inspect.isroutine(plugin):
                self.links[name] = plugin
            else:
                self.links[name] = self.install(plugin)


# Plugin loader / importer

def _import_module(name):

    # Importing anything which starts with 'stado' from stado.py zip package.
    # Without this importlib will not be able to dynamic import modules
    # from stado.py
    if IS_ZIP_PACKAGE:
        sys.path.insert(0, PATH)

    try:
        module = importlib.import_module(name)
    except ImportError:
        raise ImportError('plugin not found: ' + name)
    finally:
        # Go back to default import hierarchy.
        if IS_ZIP_PACKAGE:
            sys.path.remove(PATH)

    return module


def load_plugin(name, package='stado.plugins'):

    # For example: foo-module.bar
    if '.' in name:

        # foo.bar => module_name: foo-module, class_name: bar
        module_name, class_name = name.split('.', 1)
        module_name = module_name.replace('-', '_')
        module = _import_module(package + '.' + module_name)

        default_class = getattr(module, class_name)
        if not default_class:
            raise AttributeError('plugin {}: has no attribute {}'
                                 .format(module_name, class_name))
        return default_class

    else:
        # foo-module => foo_module
        module_name = name.replace('-', '_')
        # foo_module => FooModule
        class_name = utils.camel_case(module_name)

        module = _import_module(package + '.' + module_name)

        # Global apply() function.
        if hasattr(module, 'apply'):
            # Apply function must be callable!
            if not callable(module.apply):
                raise TypeError('plugin {}: apply attribute must be callable'
                                .format(module_name))
            return module.apply

        # Try to get default plugin class, for example if plugin module is
        # 'html.py', the default class will be 'Html'
        default_class = getattr(module, class_name)
        if default_class:

            # Error, default class object is not class!
            if not inspect.isclass(default_class):
                raise TypeError('plugin {}: default plugin class is {}'
                                .format(module_name, type(default_class)))
            return default_class

        # There is no default plugin!
        else:
            raise ImportError('plugin {}: has no default plugin class or apply '
                              'function'.format(module_name))