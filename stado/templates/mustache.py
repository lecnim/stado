#from ..libs import pystache
import pkgutil
import importlib
import os

import logging


# Support for pystache package.
path = os.path.dirname(__file__)
path = os.path.split(path)[0]
path = os.path.join(path, 'libs')

logging.warning('dDD')

from ..libs import pystache

#for loader, module_name, is_pkg in pkgutil.iter_modules([path]):
#    logging.warning('loading abslute' + module_name)
#    if module_name == 'pystache':
#        pystache = loader.find_module(module_name).load_module(module_name)
#        #pystache = importlib.import_module('.' + module_name, 'stado.libs')


# Template engine info.

enabled = True
requirements = 'Require mustache module! http://github.com/defunkt/pystache'

name = 'mustache'


class TemplateEngine:
    """This class is used to render templates."""

    def __init__(self, path):
        self.path = path

    @staticmethod
    def render(source, context):
        """Used by Renderer class."""
        return pystache.render(source, **context)
