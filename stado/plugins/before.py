import fnmatch
import inspect
from . import Plugin








class Before(Plugin):

    name = 'before'

    # PLugin must run before yaml page dump plugin.
    order = 0


    def __init__(self, site):
        Plugin.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'loader.after_loading_content': self.add_context,
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
                if fnmatch.fnmatch(content.source, path):

                    # Runs function with different arguments depending on their
                    # amount.

                    args = inspect.getfullargspec(function)[0]
                    if len(args) == 0:
                        context = function()
                    else:
                        context = function(content)

                    if context:
                        content.context.update(context)