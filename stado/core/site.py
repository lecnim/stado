import os
import inspect

from .loaders import FileSystemItemLoader
from .item import ItemTypes
from ..templates.mustache import TemplateEngine
from .events import Events
from .. import controllers
from .. import plugins
from .. import config as CONFIG
from .cache import ItemCache, DictCache
from .. import log


class Site(Events):
    """
    This is site. Use run() method to build it.

    Site building:
    - Loads items using Loaders objects and saves this items in Cache object.
    - Renders item from cache using item renderers objects.
    - Write item to file system using item deployer object.

    """

    def __init__(self, path=None, output=None, config=None,
                 template_engine=TemplateEngine,
                 cache=DictCache,
                 loaders=(FileSystemItemLoader(),)):
        """
        Arguments:
            path: Items will be created using files in this path. Default path is
                same as path to python module file using this class.
            output:
                Site will be build in this location.
            template_engine:
                Template engine class. Default is using mustache.
            cache:
                Cache class.
            loaders: List of ItemLoader classes used to create Items objects.
        """

        Events.__init__(self)


        # Set path to file path from where Site is used.
        if path is None:
            path = os.path.split(inspect.stack()[1][1])[0]

        # Configuration loading.
        self.config = CONFIG.get_default_site_config()
        if config:
            self.config.update(config)

        # Absolute path to site source directory.
        self.path = os.path.normpath(path)
        # Absolute path to site output directory.
        if output:
            self._output = output
        else:
            self._output = os.path.join(self.path, CONFIG.build_dir)

        # Paths pointing to files or directories which will be ignored.
        self.excluded_paths = []
        self.template_engine = template_engine(self.path)

        self.item_types = ItemTypes()
        self.cache = ItemCache(cache(self.output))
        self.loaders = loaders


        # Loads controllers from stado.controllers package.
        self.controllers = {}
        for i in controllers.load(self.config['controllers']):
            self.controllers[i.name] = self.bind_controller(i(self))

        # Loads plugins from stado.plugins package.
        self.plugins = {}
        for i in plugins.load(self.config['plugins']):
            self.plugins[i.name] = i(self)


    @property
    def output(self):
        if CONFIG.output:
            return CONFIG.output
        return self._output


    # Shortcuts.

    def get_item(self, item_source):
        """Shortcut for self.cache.load_item()."""
        return self.cache.load_item(item_source)

    def save_item(self, item):
        """Shortcut for self.cache.save_item()."""
        self.cache.save_item(item)

    @property
    def items(self):
        """Yields items from cache."""
        for item in self.cache:
            yield item

    @property
    def sources(self):
        """Yield items sources available in cache."""
        for source in self.cache.sources:
            yield source


    # Methods.

    def bind_controller(self, controller):
        """Binds events to given controller object. Installs controller as a site
        method if controller is callable. Returns given controller object."""

        # Bind controller as a object method.
        if controller.is_callable is True:
            setattr(self, controller.name, controller)

        self.events.subscribe(controller)
        return controller


    def run(self):
        """Creates site: loads, renders, deploys."""

        log.debug('Starting building site: {}'.format(self.path))

        # Build site.

        self.load()
        self.render()
        self.deploy()

        # Remove cache.

        self.clear()


    # Generating.

    def load(self):
        """Loads items from site source files and stores this items in cache."""

        log.debug('\tLoading site items...')

        # Controllers order.
        # Before loading:
        #   1) layout
        # After loading:
        #   1) permalink
        #   2) before

        # Use each content loader.
        for loader in self.loaders:

            # Skip site output directory.
            excluded_paths = self.excluded_paths + [self.output]
            for item in loader.load(self.path, excluded_paths):

                log.debug('\t\t[ {0.type} ]  {0.source}'.format(item))

                # Get item model with load(), render(), deploy() methods.
                # Install this methods in Item.

                model = self.item_types(item.type)
                item.set_type(model)

                # Subscribe controller to item object events.
                for i in self.controllers.values():
                    item.events.subscribe(i)

                # Loads item data and stores loaded item in cache.
                self.cache.save_item(item.load())

        return self


    def render(self):
        """Renders items to cache."""

        log.debug('\tRendering items...')

        # Controllers order.
        # Before rendering:
        #   1) helper
        # After rendering:
        #   1) layout
        #   2) helper
        #   3) after

        for item in self.cache:
            self.cache.save_item(item.render())
        return self


    def deploy(self):
        """Writes items to output directory."""

        log.debug('\tDeploying items...')

        for item in self.cache:
            log.debug('\t\t{} => {}'.format(item.source, item.output))
            item.deploy(self.output)
        return self


    # Cleaning.

    def clear(self):
        """Clearing site components."""

        #for i in self.controllers.values():
        #    del i.site
        #del self.controllers
        self.cache.clear()
