import fnmatch
from . import Controller


class Pages(Controller):

    name = 'pages'

    def __call__(self, *paths):
        """Yields Pages object from given location."""

        if self.site.cache:
            for path in paths:

                for file in self.site.cache.files:
                    if fnmatch.fnmatch(file, path):

                        content = self.site.cache[file]
                        if content.is_page():
                            yield self.site.cache[file]
