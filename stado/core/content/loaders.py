import os

from . import SiteItem
from .finders import FileSystemItemFinder
from ..events import Events



class ItemLoader(Events):
    pass



# TODO: Ideas for other finder classes.

class ZipItemLoader(ItemLoader):
    """Only idea, can load content from zip files."""
    pass

class SQLiteItemLoader(ItemLoader):
    """Only idea, can load content from SQLite database."""
    pass

class JsonItemLoader(ItemLoader):
    """Only idea, can load content from JSON database."""
    pass



# Filesystem content loader.

class FileSystemItemLoader(ItemLoader):

    finder = FileSystemItemFinder()


    def load(self, path, excluded_paths=None):

        for content_path in self.finder.search(path, excluded_paths):

            # output: Content will be written in output directory using this path.
            #   For example: "about/index.html"
            # id: Content is recognized by controllers using it is. Id is same as
            #   source path.
            output = os.path.relpath(content_path, path)
            yield FileItem(content_path, output)


class FileItem(SiteItem):

    def __init__(self, path, output):

        # File item source is same as item output. For example if source path is
        # "b.html", it be that same as a item output path: "output/b.html".

        SiteItem.__init__(self, source=output, output=output, path=path)

        # Item type is recognized using file extension.
        self.type = os.path.splitext(path)[1][1:]

        # If item content it not set - it will be read directly from file.
        self._data = None

    @property
    def data(self):
        if self._data is None:
            with open(self.path) as file:
                return file.read()
        return self._data

    @data.setter
    def data(self, value):
        self._data = value