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


    def get_content(self, content_id):
        return self.site.content.cache.load(content_id)

    def save_content(self, content):
        self.site.content.cache.save(content)


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
from . import yaml_page_dump
from . import json_page_dump


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
