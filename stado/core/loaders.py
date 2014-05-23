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
            yield FileItem(source_path, output_path)


class FileItem(SiteItem):

    def __init__(self, source_path, output_path):

        # File item source is same as item output. For example if source path is
        # "b.html", it be that same as a item output path: "output/b.html".

        SiteItem.__init__(self, source_path, output_path)

        # Item type is recognized using file extension.
        self.type = os.path.splitext(source_path)[1][1:]

        # If item content it not set - it will be read directly from file.
        self._data = None

    @property
    def source(self):
        if self._data is None:
            with open(self.source_path) as file:
                return file.read()
        return self._data

    @source.setter
    def source(self, value):
        self._data = value

    def is_source_modified(self):
        return False if self._data is None else True