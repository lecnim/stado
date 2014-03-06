from ..errors import StadoError
from ..core.events import Events


class TemplateEngine(Events):
    """Base class for template engines."""

    # Disabled engine are not used.
    enabled = True
    # Message printed if required packages are not available.
    requirements = 'Requirements not specified.'

    @classmethod
    def check_requirements(cls):
        """Checks requirements and returns True if engine is available. Should
        raises StadoError if some required packages are missing."""
        return True

    def __init__(self, path=None):
        Events.__init__(self)
        self.path = path


# All available template engines must be imported.

from .mustache import Mustache
from .jinja2 import Jinja2


def load(engine_name):
    """Returns template engine class. Raises StadoError if engine not found."""

    for i in TemplateEngine.__subclasses__():
        if i.name == engine_name and i.enabled:
            if i.check_requirements():
                return i

    raise StadoError('Template engine not found: {}'.format(engine_name))
