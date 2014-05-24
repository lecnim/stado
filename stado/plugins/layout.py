import os
import os.path
from . import Plugin, load_plugin

class Layout(Plugin):

    def __init__(self, path, engine=None, context=None):
        super().__init__()

        # auto-detect engine

        if engine is None:
            engine = os.path.splitext(path)[1][1:].lower()

        self.engine = engine
        self.path = path
        self.context = context if context else {}

    def apply(self, site, item):

        template = site.load(self.path)

        # Add site helpers
        template.context = site.helpers
        template.context['content'] = item.source
        template.context['page'] = item.context

        # Pop helpers from item context.
        helpers = {}
        for key in item._helpers:
            helpers[key] = item.context.pop(key)

        template.context.update(self.context)
        engine = site.plugins.get(self.engine)
        engine.apply(site, template)

        item.source = template.source

        for key, value in helpers.items():
            item.context[key] = value