import fnmatch
import inspect
from . import Controller


class Before(Controller):

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

                    args = inspect.getfullargspec(function)[0]
                    if len(args) == 0:
                        context = function()
                    else:
                        context = function(content)

                    if context:
                        print(content.id, content.metadata)
                        content.metadata.update(context)