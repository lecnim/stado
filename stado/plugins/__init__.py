class Plugin:
    pass


class Extension(Plugin):
    name = None
    extensions = []

    loaders = []
    renderers = []

    deployer = None


    def __init__(self, site):

        # Reference to parent Site object.
        self.site = site

        self.renderers = self._update_template_engine(self.renderers)

        # Model with supporting any extension.
        if self.extensions is None:
            self.site.item_types.set(None, self.loaders, self.renderers,
                                     self.deployer)
        else:
            for e in self.extensions:
                self.site.item_types.set(e, loaders=self.loaders,
                                         renderers=self.renderers,
                                         deployers=self.deployer)


    def _update_template_engine(self, renderers):
        """Replaces "template_engine" with TemplateEngine object, in renderers
        list."""

        return [self.site.template_engine if x == 'template_engine'
                else x for x in renderers]


# Supported files types.

from .extensions.default import Default
from .extensions.markdown import Markdown
from .extensions.html import HTML
from .extensions.json import Json
from .extensions.yaml import Yaml


def load(select=None):
    """Yields controllers modules.

    Args:
        select (None or list): Loads only given modules, or if None loads all modules.
    Yields:
        module object
    """

    for class_obj in Extension.__subclasses__():
        print(class_obj)
        if select is None or class_obj.name in select:
            yield class_obj
