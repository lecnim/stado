from . import Controller


class Helper(Controller):

    name = 'helper'
    order = 1

    def __init__(self, site):
        Controller.__init__(self, site)

        # Bind events to plugin methods.
        self.events.bind({
            'template.before_rendering': self.install,
            'template.after_rendering': self.uninstall
        })

        # Available helper methods loaded from site.py file.
        self.functions = {}

    def __call__(self, function):
        """Decorator @helper. Stores function which is decorated by @helper."""

        # Stores function as a property.
        self.functions[function.__name__] = function
        return function

    #

    def install(self, renderer, context):
        """Adds helper methods to context."""

        if getattr(renderer, 'use_helpers', True):
            for name, function in self.functions.items():

                # Do not overwrite already existing metadata variables.
                if not name in context:
                    context[name] = function

    def uninstall(self, renderer, context):
        """Removes helper methods from a context."""

        if getattr(renderer, 'use_helpers', True):

            # Use helping list, to avoid dict changing size during iteration.
            remove = []

            for key, value in context.items():
                for name, function in self.functions.items():
                    if key == name and value == function:
                        remove.append(key)
            for key in remove:
                del context[key]
