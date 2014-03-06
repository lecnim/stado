import sys
import logging

from . import libs
from . import config

__version__ = '0.6.0'
version = __version__


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




# Default app.

app = None
run = None


class WrapController:

    def __init__(self, controller):
        self.controller = controller
    def __call__(self, *args, **kwargs):
        # if not app.is_loaded:
        #     app.load()
        return self.controller(*args, **kwargs)


def default_site(path):
    global app
    global run

    app = Site(path)
    run = app.run

    module = sys.modules[__name__]

    for name, plugin in app.controllers.items():
        # setattr(module, name, plugin)

        setattr(module, name, WrapController(plugin))

def clear_default_site():
    global app
    global run

    module = sys.modules[__name__]

    for name, plugin in app.controllers.items():
        setattr(module, name, None)

    app.clear()
    app = None
    run = None



from .core.site import Site
from .console import Console





# Shortcuts for site.py
Stado = Site



# Run stado. Get arguments and pass them to console.
if __name__ == "__main__":
    console = Console()

    sys.exit(0) if console() else sys.exit(1)
