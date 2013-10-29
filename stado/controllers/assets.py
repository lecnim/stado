from . import Controller


class Assets(Controller):
    """Returns list of available assets items."""

    name = 'assets'

    def __call__(self, *paths):
        """Yields asset items from given location."""

        # Iterate all site items.
        for item in self.site.items.cache.items.values():
            # Item must be assets and source paths must match.
            if not item.is_page() and item.match(*paths):
                # Loads item form cache.
                yield self.site.items.cache.load(item.source)
