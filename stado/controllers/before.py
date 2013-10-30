"""
@before controller
"""

import inspect
from . import Controller


class Before(Controller):
    """Access to item before rendering. Usage:

    @before('a.html', 'b.html')
    def page(path):
        ...

    """

    name = 'before'
    # Should run after permalink controller.
    order = 1


    def __init__(self, site):
        Controller.__init__(self, site)

        # Bind events to controller methods.
        self.events.bind({

            # This event is use instead of item.before_rendering, because during
            # rendering all items must have updated metadata already.
            'item.after_loading': self.update_metadata,
        })

        self.functions = []


    def __call__(self, *paths):
        """Calling @before decorator."""

        def wrap(function):
            self.functions.append((function, paths))
        return wrap


    def update_metadata(self, item):
        """Updates item metadata."""

        for function, paths in self.functions:
            if item.match(*paths):

                # Runs function with different arguments depending on their
                # amount.

                args = inspect.getfullargspec(function)[0]
                if len(args) == 0:
                    metadata = function()
                else:
                    metadata = function(item)

                if metadata:
                    item.metadata.update(metadata)
