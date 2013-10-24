class Plugin:
    pass

class ContenTypePlugin(Plugin):

    name = None
    extensions = []

    loaders = []
    renderers = []
    deployers = []


    def __init__(self, site):
        self.site = site

        if self.extensions is None:
            self.site.content.types.set(None, self.loaders, self.renderers,
                                        self.deployers)
        else:
            for e in self.extensions:

                self.site.content.types.set(
                    e,
                    loaders=self.loaders,
                    renderers=self.renderers,
                    deployers=self.deployers
                )


# Supported files types.

from .extensions.default import Default
from .extensions.markdown import Markdown

def load(select=None):
    """Yields controllers modules.

    Args:
        select (None or list): Loads only given modules, or if None loads all modules.
    Yields:
        module object
    """

    for class_obj in ContenTypePlugin.__subclasses__():
        print(class_obj)
        if select is None or class_obj.name in select:
            yield class_obj
