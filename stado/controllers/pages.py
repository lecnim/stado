from . import Controller


class Pages(Controller):

    name = 'pages'

    def __call__(self, *paths):
        """Yields Pages object from given location."""

        # Iterate all site items.
        for item in self.site.items.cache.items.values():
            # Item must be assets and source paths must match.
            if item.is_page() and item.match(*paths):
                # Loads item form cache.
                yield self.site.items.cache.load(item.source)
