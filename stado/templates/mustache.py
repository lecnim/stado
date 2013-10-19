from ..libs import pystache


# Template engine info.

enabled = True
requirements = 'Require mustache module! http://github.com/defunkt/pystache'

name = 'mustache'


class TemplateEngine:
    """This class is used to render templates."""

    def __init__(self, path):
        self.path = path

    @staticmethod
    def render(source, context):
        """Used by Renderer class."""
        return pystache.render(source, **context)
