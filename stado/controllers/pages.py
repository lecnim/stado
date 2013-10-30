from . import Controller


class Pages(Controller):
    """Iterate page items."""

    name = 'pages'

    def __call__(self, *paths):
        """Yields page items from given location."""

        for item in self.site.items:
            if item.is_page() and item.match(*paths):
                yield item
