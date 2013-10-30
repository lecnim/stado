from . import Controller


class Assets(Controller):
    """Returns list of assets items."""

    name = 'assets'

    def __call__(self, *paths):
        """Yields asset items from given location."""

        for item in self.site.items:
            if not item.is_page() and item.match(*paths):
                yield item
