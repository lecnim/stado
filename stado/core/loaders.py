import os

from .item import SiteItem
from .finders import FileFinder


class ItemLoader:

    def __init__(self, path='.'):
        self.root = path

    def load(self, path, excluded=()):
        """Inherited class overrides this method."""
        pass

    def __repr__(self):
        return "{}(path={!r})".format(self.__class__.__name__, self.root)


# Filesystem content loader.


class FileLoader(ItemLoader):
    """Creates items from files."""

    # This object is used to find items in path.
    finder = FileFinder()

    def load(self, path, excluded=()):
        """Yields items created from files in given path."""

        for source_path in self.finder.find(path, excluded):
            output_path = os.path.relpath(source_path, self.root)
            # output_path = os.path.relpath(source_path, path)
            yield SiteItem(source_path, output_path)