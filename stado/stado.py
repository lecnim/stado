"""

"""

# Standard modules.
import os
import sys
import importlib
import shutil
import inspect
import re
import shelve
from collections import UserDict

# Support for importing in older python.
if sys.version_info[:2] <= (3, 2):
    import imp

# Local imports.
from . import plugins
from . import loaders
from . import templates
from . import config as CONFIG
from .events_system import Events



def get_default_config():
    """Returns dict with default configuration."""
    return {
        'destination': CONFIG.build_dir,

        'cache': 'shelve',


        'loaders': None,
        'plugins': None,
    }



# Site:

class Site:

    def __init__(self, path=None, config=None):

        # Set path to file path from where Site is used.
        if path is None:
            path = os.path.split(inspect.stack()[1][1])[0]

        # Configuration loading.
        self.config = get_default_config()
        if config:
            self.config.update(config)

        # Absolute path to site source directory.
        self.path = os.path.normpath(path)
        # Absolute path to site destination directory.
        #self._destination = os.path.join(self.path, self.config['destination'])
        self._output = os.path.join(self.path, CONFIG.build_dir)

        # Cache for storing content.
        self.cache = None

        # Main components.

        self.loader = Loader(self.path)
        self.rendered = Rendered(self.path)
        self.deployer = Deployer(self.output)

        # Plugins

        self.plugins = {}
        for class_object in plugins.load(self.config['plugins']):
            plugin = class_object(self)
            self.plugins[plugin.name] = plugin

            # Bind plugin as a object method.
            setattr(self, plugin.name, plugin)

            self.loader.events.subscribe(plugin)

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
        """Creates site: Loads, renders, deploys."""

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
        """Loads content from site files."""

        for content in self.loader.walk(exclude=[self.output]):
            # Save content in cache (where? it depends on cache type).
            self.cache[content.source] = content

        return self

    def render(self):
        """Renders content."""

        for content in self.cache.values():
            if content.is_page:
                data = self.rendered.render(content.template, content.context)
                content.template = data
                self.cache[content.source] = content

        return self

    def deploy(self):
        """Saves content to destination directory."""

        for content in self.cache.values():
            self.deployer.deploy(content.destination, content.template)




class Loader(Events):
    """

    Events:

        loader.before_loading_controller
        loader.after_loading_controller
        loader.before_loading_content
        loader.after_loading_content

    """

    def __init__(self, path, config=None):
        Events.__init__(self)

        # File will be loaded from this absolute path pointing to directory.
        self.path = os.path.normpath(path)

        # Site configuration.
        self.config = get_default_config() if config is None else config

        # Loaders.
        self.loaders = {}

        # Loaders list is get from site configuration.
        for module in loaders.load(self.config['loaders']):
            if module.enabled:
                for ext in module.inputs:
                    self.loaders[ext] = module

            # Loader is disabled, for example requirements are not met.
            else:
                pass


    def load_file(self, path):
        """Returns Content object created from file or None if loading failed."""

        # Event can cancel loading file.
        if False in self.event('loader.before_loading_content', path):
            return None

        full_path = os.path.join(self.path, path)
        ext = os.path.splitext(path)[1][1:]

        # File is supported by one of loaders.
        if ext in self.loaders:

            # Use loader to get file data.
            loader = self.loaders[ext]
            template, context = loader.load(full_path)

            # Loader modify Content destination path.
            # For example markdown loader change *.md to *.html
            if loader.output == 'html':
                content = Page(path)
            else:
                content = Asset(path)

            content.permalink = '/:path/:title.' + loader.output
            content.context = context
            content.template = template

        # File is not supported by loaders.
        else:
            content = Asset(path)

        self.event('loader.after_loading_content', content)
        return content


    def load_dir(self, path=''):
        """Yields Content objects created from files in directory."""

        full_path = os.path.join(self.path, path)
        list_dirs = os.listdir(full_path)

        # Load contents.
        for file_name in list_dirs:

            # Path must points to file, file should not be python script.
            if os.path.isfile(os.path.join(full_path, file_name)) and \
                    not file_name.endswith('.py'):
                content = self.load_file(os.path.join(path, file_name))
                if content: yield content


    def walk(self, path='', exclude=None):
        """Yields Content objects created from files in directory tree. Also
        imports controller modules depending import_controllers argument."""

        full_path = os.path.join(self.path, path)

        # Skip directory if it is excluded.
        if (not exclude) or (not full_path in exclude) and (not path in exclude):

            # Load current dir.
            for content in self.load_dir(path):
                yield content

            for directory in os.listdir(full_path):

                # Important! Skip __pycache__ directory!
                if os.path.isdir(os.path.join(full_path, directory)) \
                    and not directory == '__pycache__':
                    for content in self.walk(os.path.join(path, directory), exclude):
                        yield content




# Content events:
#
# content.before_creating
# content.after_creating
#

class Content:

    def __init__(self, source):

        self.path = source
        self.source = source
        self.filename = os.path.split(self.source)[1]

        self.permalink = '/:path/:filename'

        self.template = ''
        self.context = {}

    @property
    def destination(self):

        keywords = re.findall("(:[a-zA-z]*)", self.permalink)
        destination = os.path.normpath(self.permalink)


        items = {
            'path': os.path.split(self.source)[0],
            'filename': self.filename,
            'title': os.path.splitext(self.filename)[0],
        }

        # :filename
        for key in keywords:
            # filename
            if key[1:] in items:
                destination = destination.replace(key, str(items[key[1:]]))

        return destination.lstrip('\\')


    def __repr__(self):
        return 'Content ' + self.source




class Asset(Content):
    def is_page(self):
        return False

    def is_asset(self):
        return True

class Page(Content):
    def is_page(self):
        return True
    def is_asset(self):
        return False




# Cache.

class ShelveCache(UserDict):
    """Cache data in filesystem using shelve module."""

    def __init__(self, path):
        UserDict.__init__(self)

        self.path = os.path.join(path, '__cache__')
        os.makedirs(self.path)

        self.data = shelve.open(os.path.join(self.path, 'contents'))
        # Removes previous data.
        self.data.clear()

    def clear(self):
        self.data.close()
        shutil.rmtree(self.path)

class DictCache(dict):
    """Cache data in RAM memory using only python dict object."""

    def clear(self):
        pass



#
# {{ content }} available in layout file
#
#

class Rendered:

    def __init__(self, path, template_engine='mustache'):

        module = templates.load(template_engine)
        if module:

            if module.enabled:
                self.template_engine = module.TemplateEngine(path)

            # Template engine is disabled, for example requirements are not met.
            else:
                raise ImportError('Template engine is disabled: ' + template_engine)

        # Module file not found.
        else:
            raise ImportError('Template engine not available: ' + template_engine)


    def render(self, source, context=None):

        if context is None:
            context = {}
        if source is None:
            source = ''

        return self.template_engine.render(source, context)




class Deployer:
    def __init__(self, path):
        self.path = path

    def deploy(self, path, content):


        full_path = os.path.join(self.path, path)

        if CONFIG.output:
            full_path = os.path.join(CONFIG.output, path)



        # Create missing directories.
        os.makedirs(os.path.split(full_path)[0], exist_ok=True)

        with open(full_path, mode='w', encoding='utf-8') as file:
            file.write(content)
