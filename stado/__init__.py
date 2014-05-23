import sys
import os
import logging
import zipimport

from . import libs
from . import config

__version__ = '1.0.0a'
version = __version__


# Constants

# True if stado package is in zip file.
IS_ZIP_PACKAGE = True if isinstance(__loader__, zipimport.zipimporter) \
    else False
# Absolute path pointing to stado package.
PATH = os.path.split(os.path.dirname(__file__))[0] if IS_ZIP_PACKAGE \
    else os.path.dirname(__file__)


# Custom logger using python logging module.
def get_logger():
    """Returns stado logger."""

    logger = logging.getLogger('stado')
    logger.setLevel(config.log_level)

    # Log into console.
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    ch.setLevel('DEBUG')
    logger.addHandler(ch)
    return logger

log = get_logger()


# Default site.

site = None

def default_site(path):

    global site
    site = Site(path)

    module = sys.modules[__name__]

    # Set module functions shortcuts to site methods.
    for function in site.controllers:
        setattr(module, function.__name__, function)

def clear_default_site():

    global site
    module = sys.modules[__name__]

    # Remove module functions to site methods shortcuts.
    for function in site.controllers:
        setattr(module, function.__name__, None)

    site = None


#

from .core.site import Site
from .console import Console

# Shortcuts for site.py
Stado = Site

# Run stado. Get arguments and pass them to console.
if __name__ == "__main__":
    console = Console()

    sys.exit(0) if console() else sys.exit(1)