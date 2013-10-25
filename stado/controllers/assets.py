import fnmatch
from . import Controller


class Assets(Controller):

    name = 'assets'

    def __call__(self, *paths):
        """Yields Asset objects from given location."""

        for path in paths:
            for id in self.site.content.cache.ids:
                 if fnmatch.fnmatch(id, path):
                    content = self.get_content(id)
                    if content.is_asset():
                        yield content


        #if self.site.cache:
        #
        #    for path in paths:
        #        for file in self.site.cache.files:
        #
        #            if fnmatch.fnmatch(file, path):
        #                content = self.site.cache[file]
        #                if content.is_asset():
        #                    yield content
