import importlib
import sys

from ..core.events import Events


class Plugin(Events):
    def __init__(self, site):
        super().__init__()



def load_plugin(name):

    sys.path.insert(0, '/home/lecnim/Projects/stado/build/stado.py')
    module = importlib.import_module('stado.plugins.' + name)
    sys.path.remove('/home/lecnim/Projects/stado/build/stado.py')

    return module.Plugin

