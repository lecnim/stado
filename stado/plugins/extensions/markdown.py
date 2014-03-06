from .html import HTML
# from .. import Extension
from ...libs import markdown


def render(source, metadata):
    return markdown.markdown(source)


class Markdown(HTML):

    name = 'markdown'
    extensions = ['md', 'markdown']

    # loaders = []
    # renderers = ['template_engine', render]

    def __init__(self, site):
        HTML.__init__(self, site)

        self.renderers = [self.render]

    # @staticmethod
    def render(self, data, metadata):
        data = HTML.render(self, data, metadata)
        return markdown.markdown(data)

