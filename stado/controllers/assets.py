import fnmatch
from . import Plugin


class Assets(Plugin):

    name = 'assets'

    def __call__(self, *paths):
        """Yields Asset objects from given location."""

        if self.site.cache:

            for path in paths:
                for file in self.site.cache.files:

                    if fnmatch.fnmatch(file, path):
                        content = self.site.cache[file]
                        if content.is_asset():
                            yield content
