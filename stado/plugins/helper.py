from . import Plugin


class HelpersCollection:
    """This class is base class for class which stores all helpers methods."""
    pass


class HelperFunction:
    """Stores helper function as a property."""

    def __init__(self, function):
        self.function = function
    def __get__(self, obj, objtype):
        return self.function()


class Helper(Plugin):

    name = 'helper'

    # Plugin must be run before layout rendering.
    order = 0


    def __init__(self, site):
        Plugin.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'renderer.before_rendering_content': self.add_helpers_to_context,
            'renderer.after_rendering_content': self.remove_helpers_from_context
        })

        # Available helper methods gather from site.py file.

        self.functions = {}

        # Stores helper functions as a Class properties.
        # It is because pystache execute functions in context in different way than
        # stado supports it.

        self.properties = type('HelpersCollection', (HelpersCollection,), {})


    def __call__(self, function):
        """Decorator @helper. Stores function which is decorated by @helper."""

        # Stores function as a property.
        setattr(self.properties, function.__name__, HelperFunction(function))
        self.functions[function.__name__] = getattr(self.properties,
                                                    function.__name__)
        return function


    def add_helpers_to_context(self, content):
        """Updates content context with all available helper functions."""

        for name, function in self.functions.items():
            if not name in content.context:
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
