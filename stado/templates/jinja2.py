"""
Support for Jinja2 templates.
"""
import importlib
from . import TemplateEngine


# Template engine class.

class Jinja2(TemplateEngine):
    """Wrapper for jinja2 module."""

    name = 'jinja2'
    requirements = 'Require jinja2 module! http://jinja.pocoo.org/'
    enabled = True

    jinja2 = None


    @classmethod
    def check_requirements(cls):
        try:
            cls.jinja2 = importlib.import_module('jinja2')
            return True
        except ImportError:
            cls.enabled = False
            return False


    def __init__(self, path):
        TemplateEngine.__init__(self, path)

        loader = self.jinja2.FileSystemLoader(path)

        # Jinja2 environment set to site source path.
        self.environment = self.jinja2.Environment(loader=loader)


    def render(self, source: str, context: dict):
        """Renders source with given context."""

        template = self.environment.from_string(source)
        return template.render(**context)
