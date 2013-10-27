import fnmatch
from . import Controller


class Assets(Controller):

    name = 'assets'

    def __call__(self, *paths):
        """Yields Asset objects from given location."""

        for path in paths:
            for file in self.site.content.cache.sources:
                if fnmatch.fnmatch(file, path):
                    content = self.site.content.cache.load(file)
                    if not content.is_page():
                        yield content
