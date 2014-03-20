import importlib
import sys

from ..core.events import Events
from .. import IS_ZIP_PACKAGE, PATH


class Plugin(Events):
    def __init__(self, site):
        super().__init__()



def load_plugin(name):

    # Importing anything which starts with 'stado' from stado.py zip package.
    # Without this importlib will not be able to dynamic import modules
    # from stado.py
    if IS_ZIP_PACKAGE:
        sys.path.insert(0, PATH)

    try:
        module = importlib.import_module('stado.plugins.' + name)
    except ImportError:
        raise ImportError('plugin not found: ' + name)
    finally:
        # Go back to default import hierarchy.
        if IS_ZIP_PACKAGE:
            sys.path.remove(PATH)

    # Get plugin object.

    if hasattr(module, 'apply'):
        plugin = module.apply
    elif hasattr(module, 'Plugin'):
        plugin = module.Plugin
    else:
        raise AttributeError('module ' + name + ' is not plugin')

    return plugin

