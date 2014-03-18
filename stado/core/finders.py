"""
Finders classes. They are used to get paths pointing to files which can be uses
to create Content objects.
"""

import os
from .pathmatch import pathmatch

from ..libs import glob2 as glob


class ItemFinder:
    """Finder base class."""

    def find(self, path, excluded_paths=()):
        """Inherited class overwrites this."""
        pass


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


# TODO: Remove
# Finders.

class FileSystemItemFinder(ItemFinder):
    """
    Searches for files which can be used to create Item objects.
    """

    excluded_names = ['__pycache__', '*.py']


    def search(self, path, excluded_paths=None):
        """Yields paths pointing to files, which can be used to create Item
        objects. Argument 'excluded_paths' is list of skipped locations, relative to
        path directory.
        """

        # Add path to excluded paths. It will be easier to match them.
        if excluded_paths is None: excluded_paths = []
        excluded_paths = [os.path.join(path, e) for e in excluded_paths]

        for dirpath, folders, files in os.walk(path):

            # Skip excluded folders.
            for folder in folders:
                if self.is_excluded(folder) or pathmatch(os.path.join(dirpath,
                                                         folder), *excluded_paths):
                    folders.remove(folder)


            for file in files:
                file_path = os.path.join(dirpath, file)

                # Skip excluded files.
                if self.is_excluded(file) or pathmatch(file_path, *excluded_paths):
                    continue

                yield file_path


    def is_excluded(self, name):
        """Returns True if given name should be excluded."""

        for pattern in self.excluded_names:
            if pathmatch(name, pattern):
                return True
