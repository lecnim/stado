"""
@after controller
"""

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


    def __init__(self, site):
        Controller.__init__(self, site)

        # Bind events to controller methods.
        self.events.bind({

            # Event is run after item has finished rendering.
            'item.before_deploying': self.update_content,
        })

        self.functions = []


    def __call__(self, *paths):
        """Calling @after decorator."""

        def wrap(function):
            self.functions.append((function, paths))
        return wrap

    def update_content(self, item):
        """Updates item content."""

        for function, paths in self.functions:
            if item.match(*paths):

                # Runs function with different arguments depending on their
                # amount.

                args = len(inspect.getfullargspec(function)[0])
                if args == 0:
                    content = function()
                elif args == 1:
                    content = function(item.data)
                elif args == 2:
                    content = function(item, item.data)

                item.content = content
