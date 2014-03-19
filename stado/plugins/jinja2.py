"""
Support for Jinja2 templates.
"""
import importlib

try:
    import jinja2
except ImportError:
    raise ImportError('Require jinja2 module! http://jinja.pocoo.org/')

# Template engine class.

class Plugin:
    """Wrapper for jinja2 module."""

    name = 'jinja2'


    def __init__(self, site):

        print('JINJA!')

        loader = jinja2.FileSystemLoader(site.path)

        # Jinja2 environment set to site source path.
        self.environment = jinja2.Environment(loader=loader)


    def render(self, source: str, context: dict):
        """Renders source with given context."""

        template = self.environment.from_string(source)
        return template.render(**context)


    def apply(self, item):
        source = self.render(item.source, item.context)
        item.source = source
