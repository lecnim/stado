import sys
from .core.site import Site
from .console import Console

__version__ = '0.1.0'


# Shortcuts for site.py
Stado = Site



# Run stado. Get arguments and pass them to console.
if __name__ == "__main__":
    console = Console()

    sys.exit(0) if console() else sys.exit(1)
