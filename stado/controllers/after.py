import fnmatch
import inspect
from . import Controller


class After(Controller):
    """
    Access to item content after rendering. Use:

        @after('a.html', 'b.html')
        def method(content, item):
            ...

    """

    name = 'after'

    #TODO: remove this?
    # Controller must be run before yaml or json page dump plugin.
    order = 0


    def __init__(self, site):
        Controller.__init__(self, site)

        # Bind events to plugin methods.
        self.events.bind({

            # Event is run after item has finished rendering.
            'item.after_rendering': self.add_context,
        })

        self.functions = []


    def __call__(self, *paths):
        """Reads function and paths from decorator. Example:

        @after('a.html', 'b.html')
        def page(path):
            ...

        """

        def wrap(function):
            self.functions.append((function, paths))
        return wrap


    def add_context(self, item):

        for function, paths in self.functions:
            for path in paths:
                if fnmatch.fnmatch(item.source, path):

                    # Runs function with different arguments depending on their
                    # amount.

                    args = len(inspect.getfullargspec(function)[0])
                    if args == 0:
                        template = function()
                    elif args == 1:
                        template = function(item.data)
                    elif args == 2:
                        template = function(item, item.data)

                    item.content = template