from .html import HTMLDeployer
from .. import Extension
from ...libs import markdown


def render(source, metadata):
    return markdown.markdown(source)


class Markdown(Extension):

    name = 'markdown'
    extensions = ['md', 'markdown']

    loaders = []
    renderers = ['template_engine', render]

    deployers = HTMLDeployer



