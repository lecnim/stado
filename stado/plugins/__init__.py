import importlib
import sys

from .. import log
from .. import utils
from ..core.events import Events
from .. import IS_ZIP_PACKAGE, PATH

import inspect


class Plugin(Events):
    def __init__(self, site=None):
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

    # Get plugin classes.

    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):

            # Object is plugin only if it inherits from parent Plugin class.
            if obj != Plugin and Plugin in inspect.getmro(obj):
                return obj





    # if hasattr(module, 'apply'):
    #     plugin = module.apply
    # elif hasattr(module, 'Plugin'):
    #
    #     if Plugin in inspect.getmro()
    #
    #     plugin = module.Plugin
    #     a = inspect.getmro(plugin)
    #     print(utils.get_subclasses(plugin))
    # else:
    #     raise AttributeError('module ' + name + ' is not plugin')
    #
    # return plugin

