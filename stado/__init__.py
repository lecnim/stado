import sys
import logging

from . import libs

__version__ = '0.4.0'
version = __version__


# Custom logger from python logging module.
def get_logger():
    """Returns miniherd logger."""

    logger = logging.getLogger('stado')
    logger.setLevel(logging.DEBUG)

    # Log into console.
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    return logger

log = get_logger()




# Default app.

app = None
run = None

def default_site(path):
    global app
    global run

    app = Site(path)
    run = app.run

    module = sys.modules[__name__]

    for name, plugin in app.plugins.items():
        setattr(module, name, plugin)




from .core.site import Site
from .console import Console





# Shortcuts for site.py
Stado = Site



# Run stado. Get arguments and pass them to console.
if __name__ == "__main__":
    console = Console()

    sys.exit(0) if console() else sys.exit(1)
