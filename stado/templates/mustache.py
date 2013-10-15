from stado.libs import pystache

#from stado.libs.pystache import dumper


# Template engine info.

enabled = True
name = 'mustache'
requirements = 'Require mustache module! http://github.com/defunkt/pystache'


class TemplateEngine:
    """This class is used to render templates."""

    def __init__(self, path):
        self.path = path

    @staticmethod
    def render(source, context):
        """Used by Renderer class."""
        return pystache.render(source, **context)
