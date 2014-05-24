import os

from .item import SiteItem
from .finders import FileFinder
from .events import Events


class ItemLoader(Events):
    def load(self, path, excluded=()):
        """Inherited class overrides this method."""
        pass


# Filesystem content loader.


class FileLoader(ItemLoader):
    """Creates items from files."""

    # This object is used to find items in path.
    finder = FileFinder()

    def load(self, path, excluded=()):
        """Yields items created from files in given path."""

        for source_path in self.finder.find(path, excluded):
            output_path = os.path.relpath(source_path, path)
            yield SiteItem(source_path, output_path)