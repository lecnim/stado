import json
from . import Plugin

class JsonContext(Plugin):

    def apply(self, item):
        context = json.loads(item.source)
        item.context.update(context)


Plugin = JsonContext