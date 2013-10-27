from . import Controller


class Assets(Controller):
    """Returns list of available assets items."""

    name = 'assets'

    def __call__(self, *paths):
        """Yields Asset objects from given location."""

        # Iterate all site items.
        for item in self.site.content.cache.items.values():
            # Item must be assets and source paths must match.
            if not item.is_page() and item.match(*paths):
                # Loads item form cache.
                yield self.site.content.cache.load(item.source)
