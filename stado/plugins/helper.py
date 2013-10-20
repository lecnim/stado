from . import Plugin



class Helper(Plugin):

    name = 'helper'


    def __init__(self, site):
        Plugin.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'renderer.before_rendering_content': self.add_helpers_to_context,
            'renderer.after_rendering_content': self.remove_helpers_from_context
        })

        # Available helper methods gather from site.py file.
        self.functions = {}


    def __call__(self, function):
        """Decorator @helper. Stores function which is decorated by @helper."""

        # Stores function by its name.
        self.functions[function.__name__] = function


    def add_helpers_to_context(self, content):
        """Updates content context with all available helper functions."""

        for name, function in self.functions.items():
            content.context[name] = function

    def remove_helpers_from_context(self, content):
        """Removes all helpers methods from content context."""

        # Use helping list, to avoid dict changing size during iteration.
        remove = []

        for key, value in content.context.items():
            for name, function in self.functions.items():

                if key == name and value == function:
                    remove.append(key)

        for key in remove:
            del content.context[key]
