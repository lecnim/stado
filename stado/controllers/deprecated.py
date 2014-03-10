"""
Deprecated!
"""

# TODO: To be removed in v0.8.0

from . import Controller


class Pages(Controller):
    """Iterate page items."""

    name = 'pages'

    def __call__(self, *paths):
        """Yields page items from given location."""

        for item in self.site.items:
            if item.is_page() and item.match(*paths):
                yield item


class Assets(Controller):
    """Returns list of assets items."""

    name = 'assets'

    def __call__(self, *paths):
        """Yields asset items from given location."""

        for item in self.site.items:
            if not item.is_page() and item.match(*paths):
                yield item


import inspect
from . import Controller
from .. import log

#
class Before(Controller):
    """Deprecated!"""

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

        log.warning('Controller @before is deprecated!'
                    'Use context controller instead.')

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
