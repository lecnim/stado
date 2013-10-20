import fnmatch
import os
from . import Plugin


class Layout(Plugin):

    name = 'layout'


    def __init__(self, site):
        Plugin.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'renderer.before_rendering_content': self.render,
        })

        self.layouts = []
        self.contents = {}



    def __call__(self, path, *layouts):
        """Calling plugin."""

        # 'a.html': 'layout.html'
        self.contents[path] = layouts

        # Prevents layouts files in output.
        for i in layouts:
            self.site.ignore(i)


    def render(self, content):

        for path in self.contents:

            if fnmatch.fnmatch(content.source, path):

                for layout_path in self.contents[path]:

                    with open(os.path.join(self.site.path, layout_path)) as layout:

                        # Add {{ content }}
                        content.context['content'] = content.template
                        html = self.site.renderer.render(layout.read(), content.context)
                        content.template = html

