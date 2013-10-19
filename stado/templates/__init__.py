import pkgutil
import importlib
import os

#from stado.libs import pystache

#from . import mustache

def load(engine_name):
    """Returns template engine module."""

    # Iterate all modules in templates directory.

    path = os.path.dirname(__file__)

    print(path, engine_name)
    return importlib.import_module('.' + engine_name, 'stado.templates')

    #for loader, module_name, is_pkg in pkgutil.walk_packages([path]):
    #    print('loading', module_name)
    #
    #    if engine_name == module_name:
    #        print('GHURRA')
    #        return loader.find_module(module_name).load_module(module_name)
    #        #return importlib.import_module('.' + module_name, 'stado.templates')

    return None