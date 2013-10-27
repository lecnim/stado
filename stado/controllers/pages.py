import fnmatch
from . import Controller


class Pages(Controller):

    name = 'pages'

    def __call__(self, *paths):
        """Yields Pages object from given location."""

        for path in paths:
            for file in self.site.content.cache.sources:
                if fnmatch.fnmatch(file, path):
                    content = self.site.content.cache.load(file)
                    if content.is_page():
                        yield content
