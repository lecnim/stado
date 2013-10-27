import os
import inspect

from .content.loaders import FileSystemItemLoader
from .content import ItemManager
from ..templates.mustache import TemplateEngine
from .events import Events
from .. import controllers
from .. import plugins
from .. import config as CONFIG
from .content.cache import ShelveCache
from .. import log



class Site(Events):
    """
    This is site. It contains all sites objects like Page, Assets, Loader etc.
    Use run() method to build site.

    Site building:
    - Loads content using Loader object and saves this loaded content in Cache object.
    - Renders content from cache using Renderer object.
    - Write content to file system using Deployer object.

    """

    def __init__(self, source=None, output=None, config=None,
                 template_engine=TemplateEngine):
        Events.__init__(self)


        # Set path to file path from where Site is used.
        if source is None:
            source = os.path.split(inspect.stack()[1][1])[0]

        # Configuration loading.
        self.config = CONFIG.get_default_site_config()
        if config:
            self.config.update(config)

        # Absolute path to site source directory.
        self.path = os.path.normpath(source)
        # Absolute path to site output directory.
        if output:
            self._output = output
        else:
            self._output = os.path.join(self.path, CONFIG.build_dir)

        self.excluded_paths = []


        # Template engine used as to render Content data.
        self.template_engine = template_engine(self.path)

        # Content manager: finding content, loading, storing...
        self.content = ItemManager(
            loaders=[FileSystemItemLoader()],
            types=[],
            cache=ShelveCache(self.output)
        )


        # Controllers

        self.controllers = {}

        for c in controllers.load(self.config['controllers']):

            controller = c(self)
            self.controllers[controller.name] = controller

            # Bind controller as a object method.
            if controller.is_callable is True:
                setattr(self, controller.name, controller)

            self.events.subscribe(controller)

        # Plugins

        self.plugins = {}

        for p in plugins.load(self.config['plugins']):

            plugin = p(self)
            self.plugins[plugin.name] = plugin



    @property
    def output(self):
        if CONFIG.output:
            return CONFIG.output
        return self._output



    def run(self):
        """Creates site: loads, renders, deploys."""

        log.debug('Starting building site: {}'.format(self.path))

        # Create output directory if not exists.

        if not os.path.exists(self.output):
            os.makedirs(self.output)

        # Cache for storing content.

        self.load()
        self.render()
        self.deploy()

        # Remove cache.

        self.content.cache.clear()

        return True


    # Generating.

    def load(self):
        """Loads content from site source files to cache."""

        log.debug('\tLoading site content...')

        # Use each content loader.
        for loader in self.content.loaders:

            # Skip site output directory.
            excluded_paths = self.excluded_paths + [self.output]
            # Content loader returns Content objects.
            for content in loader.load(self.path, excluded_paths):

                log.debug('\t\t[ {0.type} ]  {0.source}'.format(content))

                # Get content model with load(), render(), deploy() methods.
                # Install this methods in Content.

                model = self.content.types(content.type)
                content.set_type(model)

                # Subscribe controller to content object events.
                for i in self.controllers.values():
                    content.events.subscribe(i)

                # Loads content data and stores loaded content in cache.

                self.event('content.before_loading', content)
                content.load()
                self.event('content.after_loading', content)

                self.content.cache.save(content)

        return self


    def render(self):
        """Renders item to cache."""

        log.debug('\tRendering content...')

        for content in self.content.cache:
            content.render()
            self.content.cache.save(content)

        return self


    def deploy(self):
        """Writes item data to output directory."""

        log.debug('\tDeploying content...')

        for content in self.content.cache:
            log.debug('\t\t{} => {}'.format(content.source, content.output))
            content.deploy(self.output)


    # Cleaning.

    def clear(self):
        """Clearing site components."""

        for i in self.controllers.values():
            del i.site
        del self.controllers
