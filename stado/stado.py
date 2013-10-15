"""

            <= Loader -> Content, Cache
    Site    <= Renderer
            <= Deployer

"""

import os
import importlib
import sys
import inspect






if sys.version_info[:2] <= (3, 2):
    import imp

import shelve
from collections import UserDict

#from stado import libs
from stado import loaders
from stado import templates

import re


def get_default_config():
    return {
        'destination': 'public',


        'loaders': None,
        'plugins': None,
    }


class Utilities:
    pass





# Events.

class EventsHandler:
    """Basic events system. How  it works:

    - Object which receives events must bind them to methods using bind()
    - Object which send events must subscribe objects which receives events using
      subscribe()
    - Object send event using notify() method.

    """

    def __init__(self):

        # List of objects with events system.
        self.subscribers = []
        # Key is event name, value is method to run when event is triggered.
        self.registered = {}

    def subscribe(self, obj):

        if not isinstance(obj.events, EventsHandler):
            raise TypeError('subscribe(x): x must supports events system')

        if not obj in self.subscribers:
            self.subscribers.append(obj)

    def notify(self, event, *args, **kwargs):

        for obj in self.subscribers:
            if event in obj.events.registered:
                yield obj.events.registered[event](*args, **kwargs)

    def bind(self, events):
        self.registered.update(events)


class Events:
    """Class should inherit this to use events system."""

    def __init__(self):
        self.events = EventsHandler()

    def event(self, name, *args, **kwargs):
        for result in self.events.notify(name, *args, **kwargs):
            yield result




# Site:

class Site:

    def __init__(self, path, config=None):

        # Configuration loading.
        self.config = config
        if config is None:
            self.config = get_default_config()

        # Absolute path to site source directory.
        self.path = os.path.normpath(path)
        # Absolute path to site destination directory.
        self.destination = os.path.join(self.path, self.config['destination'])

        self.cache = Cache()

        self.loader = Loader(self.path)
        self.rendered = Rendered(self.path)
        self.deployer = Deployer(self.destination)


    def run(self):
        """Creates site: Loads, renders, deploys."""

        self.load()
        self.render()
        self.deploy()

        return True


    def load(self):
        """Loads content from site files."""

        for content in self.loader.walk():
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
        """Returns Content object created from file."""

        self.event('loader.before_loading_content', path)

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


    def load_dir(self, path='', import_controllers=True):
        """Yields Content objects created from files in directory."""

        full_path = os.path.join(self.path, path)
        list_dirs = os.listdir(full_path)

        # Load controller.
        controller_filename = 'controller.py'
        if controller_filename in list_dirs:
            if import_controllers:
                ctrl_path = os.path.join(full_path, controller_filename)

                self.event('loader.before_loading_controller', ctrl_path)
                module = self.load_module(ctrl_path)
                self.event('loader.after_loading_controller', module)

            # Prevent loading controller file as a Content object.
            list_dirs.remove(controller_filename)

        # Load contents.
        for file_name in list_dirs:

            # Path must points to file.
            if not os.path.isdir(os.path.join(full_path, file_name)):
                yield self.load_file(os.path.join(path, file_name))


    def walk(self, path='', import_controllers=True):
        """Yields Content objects created from files in directory tree. Also
        imports controller modules depending import_controllers argument."""

        for content in self.load_dir(path, import_controllers):
            yield content

        full_path = os.path.join(self.path, path)

        for directory in os.listdir(full_path):

            # Important! Skip __pycache__ directory!
            if os.path.isdir(os.path.join(full_path, directory)) \
                and not directory == '__pycache__':
                for content in self.walk(os.path.join(path, directory),
                                         import_controllers):
                    yield content


    def load_module(self, path):
        """Returns module loaded from path pointing to python file. Module name is
        filename without extension."""

        path, filename = os.path.split(path)
        path = os.path.join(self.path, path)
        module_name = os.path.splitext(filename)[0]

        # Newer python. >= 3.3
        if sys.version_info[:2] > (3, 2):
            loader = importlib.find_loader(module_name, [path])
            return loader.load_module()

        # Older python: <= 3.2
        else:
            fp, pathname, description = imp.find_module(module_name, [path])
            return imp.load_module(module_name, fp, pathname, description)




# Content events:
#
# content.before_creating
# content.after_creating
#

class Content:

    def __init__(self, source):

        print(source)

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

class Cache(dict):
    pass


class FileCache(UserDict):

    def __init__(self, full_path):

        UserDict.__init__(self)

        self.data = shelve.open(os.path.join(full_path, '__cache__'))
        self.data.clear()



class MemoryCache(dict):
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

        print(path, full_path)

        # Create missing directories.
        os.makedirs(os.path.split(full_path)[0], exist_ok=True)

        with open(full_path, mode='w', encoding='utf-8') as file:
            file.write(content)
