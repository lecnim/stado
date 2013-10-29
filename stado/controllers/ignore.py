import fnmatch
import posixpath

from . import Controller


class Ignore(Controller):

    name = 'ignore'


    def __init__(self, site):
        Controller.__init__(self, site)

        # List of ignored paths.
        self.ignored_paths = []


    def __call__(self, *sources):

        for source in sources:

            # There are to possibilities: given ignored element is item source or
            # item object.
            if isinstance(source, str):
                if not source in self.ignored_paths:
                    self.ignored_paths.append(source)
                    self.site.excluded_paths.append(source)

            # Source is item object.
            else:
                self.site.cache.remove_item(source.source)
