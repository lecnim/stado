from ..libs import yaml
from . import Plugin

class YamlContext(Plugin):

    def apply(self, item):
        context = yaml.load(item.source)
        item.context.update(context)