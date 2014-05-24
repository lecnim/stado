"""
Support for Jinja2 templates.
"""

from . import Plugin

try:
    import jinja2
except ImportError:
    raise ImportError('Require jinja2 module! http://jinja.pocoo.org/')


# Template engine class.

class Jinja2(Plugin):
    """Wrapper for jinja2 module."""

    def install(self, site):

        # Jinja2 environment set to site source path.
        loader = jinja2.FileSystemLoader(site.path)
        env = jinja2.Environment(loader=loader)

        # Set local variables.
        return {'environment': env}

    def apply(self, site, item):
        """Renders source with given context and apply to item."""

        env = self.get_local(site, 'environment')
        template = env.from_string(item.source)
        item.source = template.render(**item.context)
