import fnmatch
import inspect
from . import Controller


class After(Controller):

    name = 'after'

    # Controller must be run before yaml or json page dump plugin.
    order = 0


    def __init__(self, site):
        Controller.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'renderer.after_rendering_content': self.add_context,
        })

        self.functions = []


    def __call__(self, *paths):
        """Reads function and paths from decorator.
        Example:

        @before('a.html', 'b.html')
        def page(path):
            ...

        Writes [page, ['a.html', 'b.html']] to self.functions.

        """

        def wrap(function):
            self.functions.append((function, paths))
        return wrap


    def add_context(self, content):

        for function, paths in self.functions:
            for path in paths:
                if fnmatch.fnmatch(content.id, path):

                    # Runs function with different arguments depending on their
                    # amount.

                    args = len(inspect.getfullargspec(function)[0])
                    if args == 0:
                        template = function()
                    elif args == 1:
                        template = function(content.data)
                    elif args == 2:
                        template = function(content, content.data)

                    content.data = template