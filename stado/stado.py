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

from stado import parsers


config = {

}


class Utilities:
    pass





# Events.

class EventsHandler:
    """Basic events system. How  it works:

    - Object which receives events must bind them to methods using bind()
    - Object which send events must subscribe objectS which receives eventS using
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









class Site:

    def __init__(self, path):

        self.loader = Loader()
        self.rendered = Rendered()
        self.deployer = Deployer()

        self.plugins = []

    def load(self):
        pass

    def deploy(self):
        pass



# TODO: Loader events
#
#   loader.before_loading_controller
#   loader.after_loading_controller
#   loader.before_loading_content
#   loader.after_loading_content
#



class Loader(Events):

    def load_dir(self, path, import_controllers=True):
        """Yields Content objects created from files in directory."""

        list_dirs = os.listdir(path)

        # Load controller.
        controller_filename = 'controller.py'
        if controller_filename in list_dirs:
            if import_controllers:
                ctrl_path = os.path.join(path, controller_filename)

                self.event('loader.before_loading_controller', ctrl_path)
                module = self.load_module(ctrl_path)
                self.event('loader.after_loading_controller', module)

            # Prevent loading controller file as a Content object.
            list_dirs.remove(controller_filename)

        # Load contents.
        for file_name in list_dirs:
            file_path = os.path.join(path, file_name)

            if not os.path.isdir(file_path):
                self.event('loader.before_loading_content', file_path)
                content = Content(file_path)
                self.event('loader.after_loading_content', file_path)

                yield content

    def walk(self, path, import_controllers=True):
        """Yields Content objects created from files in directory tree. Also
        imports controller modules depending import_controllers argument."""

        for content in self.load_dir(path, import_controllers):
            yield content

        for directory in os.listdir(path):
            dir_path = os.path.join(path, directory)

            # Important! Skip __pycache__ directory!
            if os.path.isdir(dir_path) and not directory == '__pycache__':
                for content in self.walk(dir_path, import_controllers):
                    yield content


    def load_module(self, path):
        """Returns module loaded from path pointing to python file. Module name is
        filename without extension."""

        path, filename = os.path.split(path)
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

    def __init__(self, path):

        self.path = path
        self.context = {}

    def __repr__(self):
        return self.path


class Cache(dict):
    pass


class FileCache(UserDict):

    def __init__(self, full_path):

        UserDict.__init__(self)

        self.data = shelve.open(os.path.join(full_path, '__cache__'))
        self.data.clear()



class MemoryCache(dict):
    pass



class Rendered:

    def __init__(self):

        # Load parsers.
        enabled, disabled = parsers.import_parsers()

        self.parsers = {}
        for parser in enabled:
            for ext in parser.file_extensions:
                self.parsers[ext] = parser

    def render(self):
        pass



class Parser:
    pass



class Deployer:
    pass
