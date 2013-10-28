from ..core.events import Events


class Controller(Events):
    """Base plugin class."""

    is_callable = True
    order = 10

    def __init__(self, site):
        Events.__init__(self)
        self.site = site

        # TODO: remove
        self.setup()


    def get_item(self, source):
        return self.site.content.cache.load(source)

    def save_item(self, item):
        self.site.content.cache.save(item)

    def iter_items(self):
        for i in self.site.content.cache:
            yield i


    # TODO: remove
    def setup(self):
        pass


# Plugins.

from . import ignore
from . import before
from . import after
from . import permalink
from . import helper
from . import layout
from . import pages
from . import assets


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
