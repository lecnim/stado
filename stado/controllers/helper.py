from . import Controller


class Helper(Controller):

    name = 'helper'

    # Controller must be run before layout rendering.
    order = 0


    def __init__(self, site):
        Controller.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'content.before_rendering': self.add_helpers_to_context,
            'content.after_rendering': self.remove_helpers_from_context
        })

        # Available helper methods gather from site.py file.
        self.functions = {}


    def __call__(self, function):
        """Decorator @helper. Stores function which is decorated by @helper."""

        # Stores function as a property.
        self.functions[function.__name__] = function
        return function


    def add_helpers_to_context(self, item, renderer):
        """Updates content context with all available helper functions."""

        if self.site.template_engine == renderer:

            for name, function in self.functions.items():

                #if not self.site.template_engine in item.renderers:
                #    continue

                if not name in item:
                    item.metadata[name] = function
                    print(item)

    def remove_helpers_from_context(self, item, renderer):
        """Removes all helpers methods from content context."""

        if self.site.template_engine == renderer:

            # Use helping list, to avoid dict changing size during iteration.
            remove = []

            for key, value in item.metadata.items():
                for name, function in self.functions.items():

                    if key == name and value == function:
                        remove.append(key)

            for key in remove:
                del item.metadata[key]
