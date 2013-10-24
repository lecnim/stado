from .. import ContenTypePlugin
from ...libs import markdown


class MarkdownRenderer:

    def render(self, source):
        return markdown.markdown(source)


class Markdown(ContenTypePlugin):

    name = 'markdown'
    extensions = ['md', 'markdown']

    loaders = []
    renderers = ['template_engine', MarkdownRenderer]
    deployers = []



