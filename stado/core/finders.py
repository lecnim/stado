"""
Finders classes. They are used to get paths pointing to files which can be uses
to create Item objects.
"""

import os
from ..libs import glob2 as glob


class ItemFinder:
    """Finder base class."""

    def find(self, path, excluded_paths=()):
        """Inherited class overwrites this."""
        pass

    def __repr__(self):
        return "{}".format(self.__class__.__name__)


class FileFinder(ItemFinder):
    """
    Searches for files which can be used to create site items.
    """

    def find(self, path, excluded_paths=()):
        """Yields paths pointing to files. Supports wildcards."""

        excluded_paths = [self._check_directory(i) for i in excluded_paths]
        path = self._check_directory(path)

        for path in glob.iglob(path):

            if self._is_excluded(path, excluded_paths):
                continue
            if os.path.isfile(path):
                yield path

    @staticmethod
    def _check_directory(path):
        """Appends ** wildcard to path pointing to directory. So find('dir') is
        that same as find('dir/**').
        """
        if os.path.isdir(path):
            return path + os.sep + '**'
        return path

    @staticmethod
    def _is_excluded(path, excluded_paths):
        """Returns True if path is matching one of excluded_paths."""

        for i in excluded_paths:
            if glob.fnmatch.fnmatch(path, i):
                return True
        return False