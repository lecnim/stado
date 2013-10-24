"""
Finders classes. They are used to get paths pointing to files which can be uses
to create Content objects.
"""

import os
from fnmatch import fnmatch
from ..events import Events



class ContentFinder(Events):
    """Base for classes which are used to find content."""

    def event_found_content(self, path):
        """Finder found file."""

        if False in self.event('finder.found_content', path):
            return False
        return True

    def event_found_directory(self, path):
        """Finder found directory."""

        if False in self.event('finder.found_directory', path):
            return False
        return True



# Finders.

class FileSystemContentFinder(ContentFinder):
    """
    Searches for files which can be used to create Content objects.
    """

    excluded_names = ['__pychache__']


    def search(self, path, excluded_paths=None):
        """Yields paths pointing to files, which can be used to create Content
        objects. Argument 'excluded_paths' is list of skipped locations, relative to
        path directory.
        """

        # Add path to excluded paths. It will be easier to match them.
        if excluded_paths is None: excluded_paths = []
        excluded_paths = [os.path.join(path, e) for e in excluded_paths]

        for dirpath, folders, files in os.walk(path):

            # Notify other objects that finder found folder.
            # Folder loading can be stopped by event result.
            if not self.event_found_directory(dirpath):
                continue

            # Skip excluded folders.
            for folder in folders:
                if self.is_excluded(folder) \
                    or os.path.join(dirpath, folder) in excluded_paths:
                    folders.remove(folder)

            for file in files:
                file_path = os.path.join(dirpath, file)

                # Skip excluded files.
                if self.is_excluded(file) or file_path in excluded_paths:
                    continue

                # Notify other objects that finder found file.
                # File yielding can be stopped by event result.
                if self.event_found_content(file_path):
                    yield file_path


    def is_excluded(self, name):
        """Returns True if given name should be excluded."""
        for pattern in self.excluded_names:
            return True if fnmatch(name, pattern) else False
