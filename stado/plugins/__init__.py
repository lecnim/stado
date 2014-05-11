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


# Import plugins

def _import_module(name):

    # Importing anything which starts with 'stado' from stado.py zip package.
    # Without this importlib will not be able to dynamic import modules
    # from stado.py
    if IS_ZIP_PACKAGE:
        sys.path.insert(0, PATH)

    try:
        module = importlib.import_module(name)
    except ImportError:
        raise ImportError('plugin not found: ' + name)
    finally:
        # Go back to default import hierarchy.
        if IS_ZIP_PACKAGE:
            sys.path.remove(PATH)

    return module


# TODO: Clean this!
def load_plugin(name, package='stado.plugins'):

    if '.' in name:
        module_name, class_name = name.split('.', 1)
        module_name = module_name.replace('-', '_')

        module = _import_module(package + '.' + module_name)

        default_class = getattr(module, class_name)
        if not default_class:
            raise AttributeError('Plugin has no attribute {}'.format(class_name))
        return default_class

    else:
        name = name.replace('-', '_')

        module_name = name
        class_name = utils.camel_case(name)

        module = _import_module(package + '.' + module_name)

        # Global apply() function.
        if hasattr(module, 'apply'):
            # Apply function must be callable!
            if not callable(module.apply):
                raise TypeError('plugin apply function must be callable')
            return module.apply

        # Try to get default plugin class, for example if plugin module is
        # 'html.py', the default class will be 'Html'
        default_class = getattr(module, class_name)
        if default_class:

            # Error, default class object is not class!
            if not inspect.isclass(default_class):
                raise TypeError('plugin object {} must be class, not {}'
                                .format(class_name, type(default_class)))
            return default_class

        # There is no default plugin!
        else:
            raise ImportError('Plugin module has no default plugin class')