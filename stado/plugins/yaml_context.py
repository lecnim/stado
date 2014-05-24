from ..libs import yaml
from . import Plugin

class YamlContext(Plugin):

    def apply(self, site, item):
        context = yaml.load(item.source)
        item.context.update(context)