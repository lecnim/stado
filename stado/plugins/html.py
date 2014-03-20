import os
from . import Plugin

class Html(Plugin):

    name = 'html'

    def apply(self, item):

        base_path = os.path.splitext(item.url)[0]
        item.url = base_path + '.html'

Plugin = Html