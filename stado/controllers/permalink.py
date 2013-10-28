import fnmatch
from . import Controller


# TODO: cleaning
class Permalink(Controller):

    name = 'permalink'

    def __init__(self, site):
        Controller.__init__(self, site)

        # Bind events to plugin methods.
        self.events.bind({
            'item.after_loading': self.update_permalink,
        })

        self.paths = {}

    # TODO: use url styles.
    def __call__(self, target, url):


        for item_source in self.site.content.cache.sources:
            if fnmatch.fnmatch(item_source, target):
                item = self.site.content.cache.load(item_source)
                item.url = url
                self.site.content.cache.save(item)

        self.paths[target] = url



    def update_permalink(self, item):

        for path in self.paths:

            if fnmatch.fnmatch(item.source, path):
                permalink = self.paths[path]

                if permalink == 'pretty':
                    permalink = '/:path/:name/index.html'
                elif permalink == 'default' or permalink == 'ugly':
                    permalink = '/:path/:filename'

                item.url = permalink

