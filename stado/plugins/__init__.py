from ..core.events import Events

class Plugin(Events):
    pass



class Extension(Plugin):
    name = None
    extensions = []

    url = None
    loaders = []
    renderers = []
    #
    deployer = None


    def __init__(self, site):
        Plugin.__init__(self)

        # Reference to parent Site object.
        self.site = site

        # self.renderers = self._update_template_engine(self.renderers)

        # Model with supporting any extension.
        if self.extensions is None:
            self.site.item_types.set(None, self)
        else:
            for e in self.extensions:
                self.site.item_types.set(e, self)

    def _load(self, data):
        return self.load(data)
    def load(self, data):
        return data, {}

    def _render(self, data, metadata):
        self.event('renderer.before_rendering')
        result = self.render(data, metadata)
        self.event('renderer.after_rendering')
        return result
    def render(self, data, metadata):
        return data

    def _deploy(self, data, path):
        return self.deploy(data, path)

    def deploy(self, data, path):
        return True

    # def _update_template_engine(self, renderers):
    #     """Replaces "template_engine" with TemplateEngine object, in renderers
    #     list."""
    #
    #     return [self.site.template_engine if x == 'template_engine'
    #             else x for x in renderers]


# Supported files types.

from .extensions.default import Default
from .extensions.markdown import Markdown
from .extensions.html import HTML
from .extensions.json import Json
from .extensions.yaml import Yaml



def get_subclasses(c):
    subclasses = c.__subclasses__()
    for d in list(subclasses):
        subclasses.extend(get_subclasses(d))
    return subclasses


def load(select=None):
    """Yields controllers modules.

    Args:
        select (None or list): Loads only given modules, or if None loads all modules.
    Yields:
        module object
    """

    for class_obj in get_subclasses(Extension):
        print(class_obj)
        if select is None or class_obj.name in select:
            yield class_obj
