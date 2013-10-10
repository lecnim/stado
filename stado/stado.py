

import os
import importlib
import sys

if sys.version_info[:2] <= (3, 2):
    import imp

import shelve
from collections import UserDict

from stado import parsers


config = {

}


class Utilities:
    pass

class EventsSupport:
    pass



class Site(EventsSupport):

    def __init__(self, path):

        self.loader = Loader()
        self.rendered = Rendered()
        self.deployer = Deployer()

        self.plugins = []

    def load(self):
        pass

    def deploy(self):
        pass



class Loader:

    def __init__(self, full_path):
        self.full_path = full_path



    def load(self, path='.'):


        full_path = os.path.join(self.full_path, os.path.normpath(path))
        list_dirs = os.listdir(full_path)

        # Loading controller.py
        c = 'controller.py'
        if c in list_dirs:
            self.load_controller(path)
            list_dirs.remove(c)

        # Loading contents.
        # f
        for i in list_dirs:

            rel_path = os.path.join(path, i)
            abs_path = os.path.join(full_path, i)

            # Load next directory.
            if os.path.isdir(abs_path):
                for i in self.load(rel_path):
                    yield i

            # Load file.
            else:
                yield rel_path, Content()


    def load_controller(self, path='.'):

        full_path = os.path.join(self.full_path, os.path.normpath(path))

        # Newer python. >= 3.3
        if sys.version_info[:2] > (3, 2):
            loader = importlib.find_loader('controller', [full_path])
            return loader.load_module()

        # Older python: <= 3.2
        else:
            fp, pathname, description = imp.find_module('controller', [full_path])
            return imp.load_module('controller', fp, pathname, description)


class Content:
    pass

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
