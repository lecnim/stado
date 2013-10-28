import fnmatch
import glob
import os
from . import Controller


class Layout(Controller):

    name = 'layout'


    def __init__(self, site):
        Controller.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'item.before_loading': self.add_layouts_property,
            'item.after_rendering': self.render,
        })

        # Key is path to file, value is path to layout.
        self.paths = {}



    def __call__(self, target, *layouts, **kwargs):
        """Calling plugin."""

        layout_data = (layouts, kwargs.get('context', {}))

        # Add layout data to item.
        if not isinstance(target, str):
            target.layouts = layout_data

        path = target if isinstance(target, str) else target.source

        # 'a.html': ['layout.html'], {'context': 'variables'}
        self.paths[path] = layout_data

        # Prevents layouts files in output.
        for i in layouts:
            self.site.ignore(i)


    def add_layouts_property(self, item):
        """Adds layout property to each item."""

        item.layouts = None

        for path, layout in self.paths.items():
            if item.match(path):
                item.layouts = layout
                break


    def render(self, item):
        """
        Returns template rendered using each layout. Content.template is NOT rendered.
        So this method only adds things to Content.template.
        """

        if item.layouts is not None:

            layouts, layout_metadata = item.layouts
            template = item.content

            for layout_path in layouts:
                with open(os.path.join(self.site.path, layout_path)) as layout:

                    context = {
                        'page': item.metadata,
                        'content': template
                    }
                    context.update(layout_metadata)

                    template = self.site.template_engine.render(layout.read(), context)

            item.content = template


        #
        #for path in self.paths:
        #
        #    #
        #    if not fnmatch.fnmatch(item.source, path):
        #        continue
        #
        #    layouts, layout_context = self.paths[path]
        #    template = item.template
        #
        #    for layout_path in layouts:
        #        with open(os.path.join(self.site.path, layout_path)) as layout:
        #
        #            context = {
        #                'page': item.context,
        #                'content': template
        #            }
        #            context.update(layout_context)
        #
        #            template = self.site.renderer.render(layout.read(), context)
        #
        #    return template
