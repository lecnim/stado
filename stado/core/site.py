import os
import inspect
from collections import namedtuple, OrderedDict

from functools import wraps

from .loaders import FileLoader
from .. import plugins
from .. import config as CONFIG
from .. import log
from ..utils import relative_path, is_subpath
from ..libs import glob2 as glob
from ..console import cmds


SiteRecord = namedtuple('SiteRecord',
                        ['source_path', 'output_path', 'module_path',
                         'is_default', 'is_used'])


class InstanceTracker:
    """Tracks each new Site instance."""

    def __init__(self):

        self.enabled = False
        self.records = OrderedDict()

    def __getitem__(self, item):
        return self.records[item]

    def __iter__(self):
        for i in self.records:
            yield i

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def update(self, instance):
        """Updates the record about the instance."""

        if not self.enabled:
            return False

        self.records[id(instance)] = instance.get_record()


    def dump(self, skip_unused=False):
        """Returns a list with a info about each Site instance."""

        if not self.enabled:
            raise Exception('Cannot dump() if tracker is disabled! '
                            'Enable it first!')

        if skip_unused:
            x = [i for i in self.records.values() if i.is_used]
        else:
            x = self.records.values()
        self.records = OrderedDict()
        self.disable()
        return x


def controller(function):
    """Decorator used to change method to controller."""

    function.is_controller = True

    @wraps(function)
    def wrapper(*args, **kwargs):
        # First argument of each method in Site is always self.
        site = args[0]

        # if not function in site.controllers:
        site._used_controllers.add(function)
        site.__class__._tracker.update(site)

        return function(*args, **kwargs)
    return wrapper


class Site:
    """
    This is site.
    """

    _tracker = InstanceTracker()

    def __init__(self, path=None, output=None, loader=FileLoader):
        """
        Args:
            path: Items will be created using files in this path.
                Default path is same as a python file where instance was created.
            output: Site will be build in this location.
            loaders: List of ItemLoader classes used to create Items objects.
        """

        # Is default site.
        self._is_default = False
        self._used_controllers = set()

        # Path to file where instance was created.
        self._script_path = inspect.stack()[1][1]

        # Path to site source directory.
        if path is None:
            self._path = os.path.dirname(self._script_path)
        else:
            self._path = os.path.abspath(path)

        # Absolute path to site output directory.
        if output:
            self._output = os.path.join(self.path, output)
        else:
            self._output = os.path.join(self.path, CONFIG.build_dir)

        # Paths pointing to files or directories which will be ignored.
        self.ignore_paths = [self._output]
        self.loader = loader(self.path)

        self.built_items = []
        self.helpers = {}
        self.registered = []

        # Loads plugins from stado.plugins package.
        self.plugins = plugins.PluginsManager(self)

        Site._tracker.update(self)

    def __repr__(self):
        return "{}(path={!r}, output={!r})".format(
            self.__class__.__name__, self.path, self.output)

    @property
    def path(self):
        return self._path

    @property
    def output(self):
        return self._output

    @property
    def is_used(self):
        return True if self._used_controllers else False

    def get_record(self):
        return SiteRecord(self.path, self.output, self._script_path,
                          self._is_default, self.is_used)

    # Commands.
    # Stability: 2 - Unstable

    def watch(self):

        x = cmds.watch.Watch()

        try:
            x.watch_site(self)
        except KeyboardInterrupt:
            x.cancel()
            pass

    def view(self):

        x = cmds.view.View()

        try:
            x.view_site(self)
        except KeyboardInterrupt:
            x.cancel()
            pass


    # Controllers.
    # Stability: 2 - Unstable

    # route

    @controller
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

    @controller
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

    @controller
    def find(self, path):
        """Yields items created using files in path."""

        if path == '**/*':
            ignored = [self.output, self._script_path]
        else:
            ignored = []

        path = relative_path(path)

        # Use absolute paths! Also ignored paths are absolute!
        path = os.path.join(self.path, path)
        ignored.extend([os.path.join(self.path, i) for i in self.ignore_paths])

        for item in self.loader.load(path, excluded=ignored):
            yield item

    # register

    @controller
    def register(self, path, *plugins):
        self.registered.append([relative_path(path), plugins])

    # helper

    @controller
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

    @controller
    def build(self, path='**/*', *plugins, context=None, overwrite=True):

        # TODO: build() without arguments? maybe another function to build all

        def build_item(item, plugins):

            # No plugins given, try to get registered ones.
            if not plugins:
                for pattern, plugins in self.registered:
                    if item.match(pattern):
                        self.apply(item, *plugins)

            # Backup items context, in case of custom context argument.
            x = item.context
            if context:
                item.context = context

            self.apply(item, *plugins)
            # Restore original context
            item.context = x

            # Overwrite previously build item only if it is enabled!
            if overwrite or not item.output_path in self.built_items:
                self.deploy(item)

        # String - path to file/files/directory.
        if isinstance(path, str):

            if is_subpath(os.path.join(self.path, path), self.output):
                raise ValueError('Cannot build item from output directory!')

            for item in self.find(path):
                build_item(item, plugins)

        # SiteItem object.
        else:
            build_item(path, plugins)

    def deploy(self, item):

        log.debug('Deploying item: ' + item.url)

        if not item.output_path in self.built_items:
            self.built_items.append(item.output_path)
        item.deploy(self.output)

    # apply

    @controller
    def apply(self, item, *plugins_list):
        """Uses plugins on given item. Argument plugins_list accepts string,
        Plugin class, Plugin instance or function."""

        # Add helpers to items context.
        item.install_helpers(self.helpers)

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

        item.remove_helpers()

        return item