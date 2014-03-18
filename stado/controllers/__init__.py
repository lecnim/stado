from ..core.events import Events


class Controller(Events):
    """Base controller class."""

    is_callable = True
    order = 10

    def __init__(self, site):
        Events.__init__(self)
        self.site = site

    def get_item(self):
        pass

    def modify_item(self):
        pass


# Plugins.

from . import ignore
from . import context
from . import after
from . import permalink
from . import helper
from . import layout
from . import render
from . import items
from . import deprecated

def load(select=None):
    """Yields controllers modules.

    Args:
        select (None or list): Loads only given modules, or if None loads all modules.
    Yields:
        module object
    """

    for class_obj in Controller.__subclasses__():
        if select is None or class_obj.name in select:
            yield class_obj
