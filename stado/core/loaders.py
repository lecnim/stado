import os

from .item import SiteItem
from .finders import FileSystemItemFinder
from .events import Events



class ItemLoader(Events):
    pass



# TODO: Ideas for other finder classes.

class ZipItemLoader(ItemLoader):
    """Only idea, can load items from zip files."""
    pass

class SQLiteItemLoader(ItemLoader):
    """Only idea, can load items from SQLite database."""
    pass

class JsonItemLoader(ItemLoader):
    """Only idea, can load items from JSON database."""
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

    def __init__(self, source_path, output_path):

        # File item source is same as item output. For example if source path is
        # "b.html", it be that same as a item output path: "output/b.html".

        SiteItem.__init__(self, id=output_path, output_path=output_path, source_path=source_path)

        # Item type is recognized using file extension.
        self.type = os.path.splitext(source_path)[1][1:]

        # If item content it not set - it will be read directly from file.
        self._data = None

    @property
    def source(self):
        if self._data is None:
            with open(self.source_path) as file:
                print('READING', self.source_path)
                return file.read()
        return self._data

    @source.setter
    def source(self, value):
        self._data = value

    def has_data(self):
        return False if self._data is None else True
