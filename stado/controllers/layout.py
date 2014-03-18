import os
from . import Controller


class Layout(Controller):

    name = 'layout'
    order = 0


    def __init__(self, site):
        Controller.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'item.before_loading': self.add_layouts_property,
            'item.before_rendering': self.before_rendering,
            'item.after_rendering': self.after_rendering,
        })

        # # Key is path to file, value is path to layout.
        # self.paths = {}
        #
        # self.default = None

        self.current_item = None



    def __call__(self, target, *layouts, **kwargs):
        """Calling plugin."""

        layout_data = (layouts, kwargs.get('context', {}))

        # Set default layout for all pages.
        if not layouts:

            for item in self.site.items:
                if item.is_page():
                    item.layouts = [(target,), kwargs.get('context', {})]
                    self.site.cache.save_item(item)

            self.site.ignore(target)

        else:

            if isinstance(target, str):

                for item in self.site._get(target):
                    item.layouts = layout_data
                    self.site.save_item(item)

            else:

                target.layouts = layout_data
                self.site.save_item(target)

            # Prevents layouts files in output.
            for i in layouts:
                self.site.ignore(i)


    def add_layouts_property(self, item):
        """Adds layout property to each item."""

        if not hasattr(item, 'layouts'):
            item.layouts = None
            self.site.save_item(item)




    def before_rendering(self, item):
        self.current_item = item

        item.renderers += [self.render]

    def after_rendering(self, item, data):
        self.current_item = None

        item.renderers.remove(self.render)
        return data


    def render(self, data, metadata):
        """
        Returns template rendered using each layout.
        """

        if self.current_item.layouts is not None:

            layouts, layout_metadata = self.current_item.layouts
            template = data

            for layout_path in layouts:
                with open(os.path.join(self.site.path, layout_path)) as layout:

                    context = {
                        'page': metadata,
                        'content': template
                    }
                    context.update(layout_metadata)

                    template = self.site.template_engine.render(layout.read(), context)

            return template
        return data
