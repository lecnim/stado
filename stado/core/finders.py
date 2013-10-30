"""
Finders classes. They are used to get paths pointing to files which can be uses
to create Content objects.
"""

import os
from .events import Events
from .pathmatch import pathmatch



class ItemFinder(Events):
    """Base for classes which are used to find items."""
    pass


# Finders.

class FileSystemItemFinder(ItemFinder):
    """
    Searches for files which can be used to create Item objects.
    """

    excluded_names = ['__pychache__', '*.py']


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
