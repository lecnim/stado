"""
render controller
"""

import os
from . import Controller


class RenderFile(Controller):
    """Returns rendered content from file."""

    name = 'render_file'


    def __call__(self, path, context=None):
        """Calling render controller."""

        if context is None: context = {}

        path = os.path.join(self.site.path, path)

        with open(path) as file:
            return self.site.template_engine.render(file.read(), context)
