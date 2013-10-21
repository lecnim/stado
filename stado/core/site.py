import os
import inspect

from .events import Events
from .. import plugins
from .. import config as CONFIG
from .loader import Loader
from .renderer import Rendered
from .deployer import Deployer
from .cache import DictCache, ShelveCache



class Site(Events):
    """
    This is site. It contains all sites objects like Page, Assets, Loader etc.
    Use run() method to build site.

    Site building:
    - Loads content using Loader object and saves this loaded content in Cache object.
    - Renders content from cache using Renderer object.
    - Write content to file system using Deployer object.

    """

    def __init__(self, path=None, config=None):
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
        self._output = os.path.join(self.path, CONFIG.build_dir)

        # Cache for storing content.
        self.cache = None

        # Main components.

        self.loader = Loader(self.path)
        self.renderer = Rendered(self.path)
        self.deployer = Deployer(self.output)

        # Plugins

        self.plugins = {}
        for class_object in plugins.load(self.config['plugins']):
            plugin = class_object(self)
            self.plugins[plugin.name] = plugin

            # Bind plugin as a object method.
            if plugin.is_callable is True:
                setattr(self, plugin.name, plugin)

            self.loader.events.subscribe(plugin)
            self.events.subscribe(plugin)

    @property
    def output(self):
        if CONFIG.output:
            return CONFIG.output
        return self._output

    @output.setter
    def output(self, value):
        self._output = value
        self.deployer.path = value


    def run(self):
        """Creates site: loads, renders, deploys."""

        # Create output directory if not exists.

        if not os.path.exists(self.output):
            os.makedirs(self.output)

        # Cache for storing content.

        if self.config['cache'] == 'dict':
            self.cache = DictCache()
        elif self.config['cache'] == 'shelve':
            self.cache = ShelveCache(self.output)

        self.load()
        self.render()
        self.deploy()

        # Remove cache.

        self.cache.clear()

        return True


    def load(self):
        """Loads content from site source files to cache."""

        for content in self.loader.walk(exclude=[self.output]):
            # Save content in cache (where? it depends on cache type).
            self.cache[content.source] = content

        return self


    def render(self):
        """Renders content in cache."""

        for content in self.cache.values():
            if content.is_page():

                template = content.template

                # Render using template from event.
                for result in self.event('renderer.before_rendering_content',
                                         content):

                    # Some plugin overwrite content.template.
                    if result is not None:
                        template = result
                    elif result is False:
                        continue

                data = self.renderer.render(template, content.context)

                # TODO: Something better storing content than this.
                content._content = data

                self.event('renderer.after_rendering_content', content)
                self.cache[content.source] = content

        return self


    def deploy(self):
        """Saves content from cache to output directory."""

        for content in self.cache.values():

            if content.is_page():
                self.deployer.deploy(content.output, content._content)
            else:
                source = os.path.join(self.path, content.source)
                self.deployer.copy(source, content.output)

