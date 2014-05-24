from ..libs import markdown
from . import Plugin


class Markdown(Plugin):

    def apply(self, site, item):
        item.source = markdown.markdown(item.source)

    def render(self, source):
        return markdown.markdown(source)