import fnmatch
import inspect
from . import Controller


class Before(Controller):
    """Access to item before rendering. Usage:

    @before('a.html', 'b.html')
        def page(path):
            ...

    """

    name = 'before'

    # Controller must run before yaml page dump plugin.
    order = -1


    def __init__(self, site):
        Controller.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'renderer.before_rendering_content': self.add_context,
        })

        self.functions = []


    def __call__(self, *paths):
        """Calling decorator."""

        def wrap(function):
            self.functions.append((function, paths))
        return wrap


    def add_context(self, content):

        for function, paths in self.functions:
            for path in paths:
                if fnmatch.fnmatch(content.source, path):

                    # Runs function with different arguments depending on their
                    # amount.

                    args = inspect.getfullargspec(function)[0]
                    if len(args) == 0:
                        context = function()
                    else:
                        context = function(content)

                    if context:
                        content.metadata.update(context)