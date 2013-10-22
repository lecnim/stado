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

        # Key is path to file, value is path to layout.
        self.paths = {}



    def __call__(self, target, *layouts, **kwargs):
        """Calling plugin."""

        path = target if isinstance(target, str) else target.source

        # 'a.html': 'layout.html'
        self.paths[path] = (layouts, kwargs.get('context', {}))

        # Prevents layouts files in output.
        for i in layouts:
            self.site.ignore(i)


    def render(self, content):
        """
        Returns template rendered using each layout. Content.template is NOT rendered.
        So this method only adds things to Content.template.
        """

        for path in self.paths:

            #
            if not fnmatch.fnmatch(content.source, path):
                continue

            layouts, layout_context = self.paths[path]
            template = content.template

            for layout_path in layouts:
                with open(os.path.join(self.site.path, layout_path)) as layout:

                    context = {
                        'page': content.context,
                        'content': template
                    }
                    context.update(layout_context)

                    template = self.site.renderer.render(layout.read(), context)

            return template
