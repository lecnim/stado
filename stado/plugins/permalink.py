import fnmatch
from . import Plugin


class Permalink(Plugin):

    name = 'permalink'

    def __init__(self, site):
        Plugin.__init__(self, site)

        # Bind events to plugin methods.
        self.events.bind({
            'loader.after_loading_content': self.update_permalink,
        })

        self.paths = {}

    def __call__(self, target, url):

        path = target if isinstance(target, str) else target.source
        self.paths[path] = url

    def update_permalink(self, content):

        for path in self.paths:

            if fnmatch.fnmatch(content.source, path):
                permalink = self.paths[path]

                if permalink == 'pretty':
                    permalink = '/:path/:name/index.html'
                elif permalink == 'default' or permalink == 'ugly':
                    permalink = '/:path/:filename'

                content.permalink = permalink

