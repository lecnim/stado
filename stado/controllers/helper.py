from . import Controller


class Helper(Controller):

    name = 'helper'
    order = 1


    def __init__(self, site):
        Controller.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'renderer.before_rendering': self.add_helpers,
            'renderer.after_rendering': self.remove_helpers
        })

        # Available helper methods gather from site.py file.
        self.functions = {}


    def __call__(self, function):
        """Decorator @helper. Stores function which is decorated by @helper."""

        # Stores function as a property.
        self.functions[function.__name__] = function
        return function


    def add_helpers(self, item, renderer):
        """Updates item metadata with all available helper functions."""

        # Add helper methods only when renderer is template engine, because
        # other renderers do not accepts methods in metadata dict.

        if self.site.template_engine == renderer:
            for name, function in self.functions.items():

                # Do not overwrite already existing metadata variables.
                if not name in item:
                    item.metadata[name] = function

    def remove_helpers(self, item, renderer):
        """Removes all helpers methods from item metadata."""

        if self.site.template_engine == renderer:

            # Use helping list, to avoid dict changing size during iteration.
            remove = []

            for key, value in item.metadata.items():
                for name, function in self.functions.items():
                    if key == name and value == function:
                        remove.append(key)

            for key in remove:
                del item.metadata[key]
