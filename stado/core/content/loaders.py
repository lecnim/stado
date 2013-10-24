import os

from . import Content, ContentData
from .finders import FileSystemContentFinder
from ..events import Events



class ContentLoader(Events):
    pass



# TODO: Ideas for other finder classes.

class ZipContentLoader(ContentLoader):
    """Only idea, can load content from zip files."""
    pass

class SQLiteContentLoader(ContentLoader):
    """Only idea, can load content from SQLite database."""
    pass

class JsonContentLoader(ContentLoader):
    """Only idea, can load content from JSON database."""
    pass



# Filesystem content loader.

class FileSystemContentLoader(ContentLoader):

    finder = FileSystemContentFinder()


    def load(self, path, excluded_paths=None):

        for content_path in self.finder.search(path, excluded_paths):

            # output: Content will be written in output directory using this path.
            #   For example: "about/index.html"
            # id: Content is recognized by controllers using it is. Id is same as
            #   source path.
            output = os.path.relpath(content_path, path)
            yield FileContent(content_path, output, id=output)


class FileContent(ContentData):

    def __init__(self, path, output, id):
        ContentData.__init__(self, path, output, id=id)

        self.type = os.path.splitext(path)[1][1:]
        self._data = None

    @property
    def data(self):
        if self._data is None:
            with open(self.source) as file:
                return file.read()
        return self._data

    @data.setter
    def data(self, value):
        self._data = value