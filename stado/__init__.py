import sys
import os
import logging
import zipimport
import inspect

from . import libs
from . import config

__version__ = '1.0.0a'
version = __version__


# Minimum supported python: 3.2
if sys.hexversion < 0x030200F0:
    raise ImportError('Python < 3.2 not supported!')

# Constants

# True if stado package is in zip file.
if sys.hexversion < 0x030300F0:
    if __file__.endswith(os.path.join('stado.py', 'stado', '__init__.py')):
        IS_ZIP_PACKAGE = True
    else:
        IS_ZIP_PACKAGE = False
else:
    IS_ZIP_PACKAGE = True if isinstance(__loader__, zipimport.zipimporter) \
        else False

# Absolute path pointing to stado package.
PATH = os.path.split(os.path.dirname(__file__))[0] if IS_ZIP_PACKAGE \
    else os.path.dirname(__file__)


# Custom logger using python logging module.

class Formatter(logging.Formatter):
    def format(self, record):
        if record.levelname == 'DEBUG':
            return '  ' + logging.Formatter.format(self, record)
        return logging.Formatter.format(self, record)

def get_logger():
    """Returns stado logger."""

    logger = logging.getLogger('stado')
    logger.setLevel(config.log_level)

    # Log into console.
    ch = logging.StreamHandler()
    ch.setFormatter(Formatter())
    ch.setLevel('DEBUG')
    logger.addHandler(ch)
    return logger

log = get_logger()


# Default site.

site = None

def default_site(path):

    global site
    site = Site(os.path.dirname(path))
    site._is_default = True
    site._script_path = path
    # TODO: Maybe another tracker update here?

    module = sys.modules[__name__]

    # # Set module functions shortcuts to site methods.
    # for function in site.controllers:
    #     setattr(module, function.__name__, function)

    for i in inspect.getmembers(site, predicate=inspect.ismethod):

        name, func = i

        if hasattr(func, 'is_controller'):
            setattr(module, func.__name__, func)

def clear_default_site():

    global site
    module = sys.modules[__name__]

    # Remove module functions to site methods shortcuts.
    # for function in site.controllers:
    #     setattr(module, function.__name__, None)

    for i in inspect.getmembers(site, predicate=inspect.ismethod):
        name, func = i
        if hasattr(func, 'is_controller'): setattr(module, func.__name__, None)

    site = None


#

from .core.site import Site
from .core.item import Item, FileItem
from .console import Console

# Shortcuts for site.py
Stado = Site

# Run stado. Get arguments and pass them to console.
if __name__ == "__main__":
    console = Console()

    sys.exit(0) if console() else sys.exit(1)