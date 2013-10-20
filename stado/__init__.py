import sys
import logging

from . import libs


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



from .core.site import Site
from .console import Console

__version__ = '0.1.0'






# Shortcuts for site.py
Stado = Site



# Run stado. Get arguments and pass them to console.
if __name__ == "__main__":
    console = Console()

    sys.exit(0) if console() else sys.exit(1)
