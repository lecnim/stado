from ..libs import markdown
from . import Plugin


def apply(item):
    item.source = markdown.markdown(item.source)

def render(source):
    return markdown.markdown(source)