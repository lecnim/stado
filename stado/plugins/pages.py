import fnmatch
from . import Plugin


class Pages(Plugin):

    name = 'pages'

    def __call__(self, *paths):
        """Yields Pages object from given location."""

        if self.site.cache:

            for path in paths:
                for file in self.site.cache.files:
                    if fnmatch.fnmatch(file, path):
                        yield self.site.cache[file]
