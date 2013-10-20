import inspect
from ..core.events import Events


class Plugin(Events):
    """Base plugin class."""

    def __init__(self, site):
        Events.__init__(self)
        self.site = site
        self.setup()

    def setup(self):
        pass


# Plugins.

from . import ignore
from . import before


def load(select=None):
    """Yields plugins modules.

    Args:
        select (None or list): Loads only given modules, or if None loads all modules.
    Yields:
        module object
    """

    for key, module in globals().items():
        if inspect.ismodule(module) and key != 'inspect':
            if select is None or module.name in select:

                for class_name, class_obj in inspect.getmembers(module,
                                                                inspect.isclass):
                    if class_name is not 'Plugin':
                        yield class_obj

