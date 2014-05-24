import os
import inspect

from .loaders import FileLoader
from .events import Events
from .. import plugins
from .. import config as CONFIG
from .. import log
from ..utils import relative_path
from ..libs import glob2 as glob


class Site(Events):
    """
    This is site. Use run() method to build it.

    Site building:
    - Loads items using Loaders objects and saves this items in Cache object.
    - Renders item from cache using item renderers objects.
    - Write item to file system using item deployer object.

    """

    def __init__(self, path=None, output=None, loader=FileLoader()):
        """
        Arguments:
            path: Items will be created using files in this path. Default path is
                same as path to python module file using this class.
            output:
                Site will be build in this location.
            loaders: List of ItemLoader classes used to create Items objects.
        """

        Events.__init__(self)

        # Set path to file path from where Site is used.
        if path is None:
            path = os.path.split(inspect.stack()[1][1])[0]

        # Absolute path to site source directory.
        self.path = os.path.normpath(path)
        # Absolute path to site output directory.
        if output:
            self._output = output
        else:
            self._output = os.path.join(self.path, CONFIG.build_dir)

        # Paths pointing to files or directories which will be ignored.
        self.excluded_paths = []
        self.loader = loader

        self.built_items = []
        self.helpers = {}
        self.registered = []

        # Loads plugins from stado.plugins package.
        self.plugins = plugins.PluginsManager(self)

        # This methods are used in default site.
        self.controllers = [
            self.build,
            self.register,
            self.route,
            self.find,
            self.load,
            self.apply
        ]

    @property
    def output(self):
        if CONFIG.output:
            return CONFIG.output
        return self._output

    # Controllers
    # Stability: 2 - Unstable

    # route

    def route(self, url, source):

        log.debug('Adding route: ' + url)

        path = os.path.join(self.output, url.lstrip('/'))

        # Url is directory.
        # /about => /about/index.html
        extension = os.path.splitext(path)[1]
        if not extension:
            path = path + '/' + 'index.html'

        # Create missing directories.
        base_path = os.path.split(path)[0]
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        if callable(source):
            source = source()

        with open(path, 'w') as page:
            page.write(source)

    # load

    def load(self, path):
        """Returns list of items created using files in path."""

        path = relative_path(path)

        # Errors:

        if glob.has_magic(path):
            raise ValueError('load() do not support wildcards: ' + path)

        if os.path.isdir(os.path.join(self.path, path)):
            raise ValueError('argument path should points to file, '
                             'not directory:')

        if not os.path.exists(os.path.join(self.path, path)):
            raise IOError('Path not found: ' + path)

        items = [i for i in self.find(path)]
        return items[0]

    # find

    def find(self, path):
        """Yields items created using files in path."""

        path = relative_path(path)

        # Use absolute paths! Also excluded paths are absolute!
        path = os.path.join(self.path, path)

        excluded = [os.path.join(self.path, i) for i in self.excluded_paths]

        for item in self.loader.load(path, excluded=excluded):
            item.output_path = os.path.relpath(item.source_path, self.path)
            # FIXME: correct default output path
            item._default_output = item.output_path
            yield item

    # register

    def register(self, path, *plugins):
        self.registered.append([relative_path(path), plugins])

    # helper

    def helper(self, function):
        self.helpers[function.__name__] = function

    def _install_helpers(self, item):
        """Adds helpers to items context. Returns list of added helpers keys."""

        x = []
        for key, value in self.helpers.items():
            # Do not overwrite existing variables.
            if not key in item.context:
                item.context[key] = value
                x.append(key)
        return x

    def _remove_helpers(self, item, helpers):
        """Removes helpers from items context."""
        for key in helpers:
            if key in item.context:
                del item.context[key]

    # build

    def build(self, path='**/*', *plugins, context=None, overwrite=True):

        # TODO: build() without arguments? maybe another function to build all

        def build_item(item, plugins):

            # Add helpers to items context.
            item.install_helpers(self.helpers)

            if not plugins:

                for pattern, plugins in self.registered:
                    if item.match(pattern):
                        self.apply(item, *plugins)

            if context:
                # TODO: Ok? What when item is build again?
                item.context = context
            self.apply(item, *plugins)

            item.remove_helpers()

            if overwrite or not item.output_path in self.built_items:
                self.deploy(item)

        # string
        if isinstance(path, str):
            for item in self.find(path):
                build_item(item, plugins)

        # item
        else:
            build_item(path, plugins)

    def deploy(self, item):

        log.debug('Deploying item: ' + item.url)

        if not item.output_path in self.built_items:
            self.built_items.append(item.output_path)
        item.deploy(self.output)


    def apply(self, item, *plugins_list):
        """Uses plugins on given item. Argument plugins_list accepts string,
        Plugin class, Plugin instance or function."""

        for i in plugins_list:

            # Plugin as a function or method. Do not install it, just execute.
            if inspect.isroutine(i):
                i(item)

            # Plugin as a string, class or Plugin instance.
            else:
                plugin = self.plugins.get(i)

                # Plugin can be also function or method!
                if callable(plugin):
                    plugin(item)
                else:
                    plugin.apply(self, item)

        return item