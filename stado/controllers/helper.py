from . import Controller


class Helper(Controller):

    name = 'helper'
    order = 1


    def __init__(self, site):
        Controller.__init__(self, site)

        # Events in plugin objects will trigger this controller methods.
        # for plugin in site.plugins.values():
        #     if getattr(plugin, 'use_helpers', True):
        #         self.events.subscribe(plugin)


        # Bind events to plugin methods.
        self.events.bind({
            # 'renderer.before_rendering': self.add_helpers,
            # 'renderer.after_rendering': self.remove_helpers,
            'template.before_rendering': self.add_helpers2,
            'template.after_rendering': self.remove_helpers2
        })

        # Available helper methods gather from site.py file.
        self.functions = {}


    def __call__(self, function):
        """Decorator @helper. Stores function which is decorated by @helper."""

        # Stores function as a property.
        self.functions[function.__name__] = function
        return function


    def add_helpers2(self, renderer, context):

        if getattr(renderer, 'use_helpers', True):
            for name, function in self.functions.items():

                # Do not overwrite already existing metadata variables.
                if not name in context:
                    context[name] = function

    def remove_helpers2(self, renderer, context):

        if getattr(renderer, 'use_helpers', True):

            # Use helping list, to avoid dict changing size during iteration.
            remove = []

            for key, value in context.items():
                for name, function in self.functions.items():
                    if key == name and value == function:
                        remove.append(key)

            for key in remove:
                del context[key]



    def add_helpers(self, item, renderer):
        """Updates item metadata with all available helper functions."""

        # Add helper methods only when renderer is template engine, because
        # other renderers do not accepts methods in metadata dict.

        if getattr(renderer, 'use_helpers', True):
            for name, function in self.functions.items():

                # Do not overwrite already existing metadata variables.
                if not name in item:
                    item.metadata[name] = function

    def remove_helpers(self, item, renderer):
        """Removes all helpers methods from item metadata."""

        if getattr(renderer, 'use_helpers', True):

            # Use helping list, to avoid dict changing size during iteration.
            remove = []

            for key, value in item.metadata.items():
                for name, function in self.functions.items():
                    if key == name and value == function:
                        remove.append(key)

            for key in remove:
                del item.metadata[key]
